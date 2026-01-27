"""
Notification service for SoloCheck.

This module handles sending push notifications via FCM and emails via SendGrid,
as well as logging notification delivery status.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session

from src.config import settings
from src.contacts.models import EmergencyContact
from src.notifications.models import NotificationLog
from src.notifications.templates import (
    get_contact_registration_email,
    get_personal_message_email,
    get_reminder_push,
    get_status_alert_email,
    get_urgent_reminder_push,
)
from src.users.models import User

logger = logging.getLogger(__name__)

# Firebase Admin SDK (lazy initialization)
_firebase_initialized = False


def init_firebase() -> bool:
    """
    Initialize Firebase Admin SDK for FCM.

    Returns:
        bool: True if initialization successful, False otherwise.
    """
    global _firebase_initialized

    if _firebase_initialized:
        return True

    if not settings.fcm_credentials_path:
        logger.warning("FCM credentials path not configured")
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(settings.fcm_credentials_path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return False


def send_push_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> bool:
    """
    Send a push notification via Firebase Cloud Messaging.

    Args:
        fcm_token: The recipient's FCM token.
        title: Notification title.
        body: Notification body text.
        data: Optional data payload.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    if not init_firebase():
        logger.warning("Firebase not initialized, skipping push notification")
        return False

    if not fcm_token:
        logger.warning("No FCM token provided, skipping push notification")
        return False

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=fcm_token,
        )

        response = messaging.send(message)
        logger.info(f"Push notification sent: {response}")
        return True
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
) -> bool:
    """
    Send an email via SendGrid.

    Args:
        to_email: Recipient email address.
        subject: Email subject.
        html_content: HTML email content.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    if not settings.sendgrid_api_key:
        logger.warning("SendGrid API key not configured, skipping email")
        return False

    try:
        message = Mail(
            from_email=settings.sendgrid_from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)

        if response.status_code in (200, 201, 202):
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return True
        else:
            logger.error(f"Email send failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def log_notification(
    db: Session,
    user_id: str,
    contact_id: str,
    notification_type: str,
    status: str,
    error_message: Optional[str] = None,
) -> NotificationLog:
    """
    Log a notification delivery attempt.

    Args:
        db: Database session.
        user_id: The user who triggered the notification.
        contact_id: The emergency contact who received it.
        notification_type: Type of notification ('status_alert' or 'personal_message').
        status: Delivery status ('pending', 'sent', or 'failed').
        error_message: Optional error message if failed.

    Returns:
        NotificationLog: The created log entry.
    """
    log_entry = NotificationLog(
        user_id=user_id,
        contact_id=contact_id,
        type=notification_type,
        status=status,
        error_message=error_message,
        sent_at=datetime.now(timezone.utc) if status == "sent" else None,
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return log_entry


def send_status_alert(
    db: Session,
    user: User,
    contact: EmergencyContact,
    days_since_checkin: int,
) -> bool:
    """
    Send a status alert to an emergency contact.

    This alert notifies the contact that the user hasn't checked in
    for the specified number of days.

    Args:
        db: Database session.
        user: The user who hasn't checked in.
        contact: The emergency contact to notify.
        days_since_checkin: Number of days since last check-in.

    Returns:
        bool: True if notification was sent successfully.
    """
    # Only send to email contacts for now
    if contact.contact_type != "email":
        logger.info(f"Contact {contact.id} is not email type, skipping")
        return False

    # Generate email content
    email_data = get_status_alert_email(
        nickname=user.nickname or "사용자",
        contact_name=contact.name,
        days=days_since_checkin,
    )

    # Send the email
    success = send_email(
        to_email=contact.contact_value,
        subject=email_data["subject"],
        html_content=email_data["html"],
    )

    # Log the notification
    log_notification(
        db=db,
        user_id=user.id,
        contact_id=contact.id,
        notification_type="status_alert",
        status="sent" if success else "failed",
        error_message=None if success else "Failed to send email",
    )

    return success


def send_personal_message_alert(
    db: Session,
    user: User,
    contact: EmergencyContact,
    message: str,
) -> bool:
    """
    Send the user's personal message to an emergency contact.

    Args:
        db: Database session.
        user: The user whose message is being sent.
        contact: The emergency contact to receive the message.
        message: The decrypted personal message content.

    Returns:
        bool: True if notification was sent successfully.
    """
    # Only send to email contacts for now
    if contact.contact_type != "email":
        logger.info(f"Contact {contact.id} is not email type, skipping")
        return False

    # Generate email content
    email_data = get_personal_message_email(
        nickname=user.nickname or "사용자",
        contact_name=contact.name,
        message=message,
    )

    # Send the email
    success = send_email(
        to_email=contact.contact_value,
        subject=email_data["subject"],
        html_content=email_data["html"],
    )

    # Log the notification
    log_notification(
        db=db,
        user_id=user.id,
        contact_id=contact.id,
        notification_type="personal_message",
        status="sent" if success else "failed",
        error_message=None if success else "Failed to send email",
    )

    return success


def send_checkin_reminder(user: User, days_remaining: int) -> bool:
    """
    Send a check-in reminder push notification to the user.

    Args:
        user: The user to remind.
        days_remaining: Days until check-in deadline.

    Returns:
        bool: True if notification was sent successfully.
    """
    if not user.fcm_token:
        logger.info(f"User {user.id} has no FCM token, skipping reminder")
        return False

    push_data = get_reminder_push(days_remaining)

    return send_push_notification(
        fcm_token=user.fcm_token,
        title=push_data["title"],
        body=push_data["body"],
        data={"type": "checkin_reminder", "days_remaining": str(days_remaining)},
    )


def send_urgent_reminder(user: User) -> bool:
    """
    Send an urgent check-in reminder push notification.

    This is sent when the user is in the grace period.

    Args:
        user: The user to remind urgently.

    Returns:
        bool: True if notification was sent successfully.
    """
    if not user.fcm_token:
        logger.info(f"User {user.id} has no FCM token, skipping urgent reminder")
        return False

    push_data = get_urgent_reminder_push()

    return send_push_notification(
        fcm_token=user.fcm_token,
        title=push_data["title"],
        body=push_data["body"],
        data={"type": "urgent_reminder"},
    )


def send_contact_registration_notification(
    user: User,
    contact: EmergencyContact,
) -> bool:
    """
    Send a notification to a newly registered emergency contact.

    This notifies the contact that they've been added as an emergency contact.

    Args:
        user: The user who added the contact.
        contact: The newly added emergency contact.

    Returns:
        bool: True if notification was sent successfully.
    """
    # Only send to email contacts
    if contact.contact_type != "email":
        return False

    email_data = get_contact_registration_email(
        user_nickname=user.nickname or "사용자",
        contact_name=contact.name,
    )

    return send_email(
        to_email=contact.contact_value,
        subject=email_data["subject"],
        html_content=email_data["html"],
    )


def send_checkin_reminder_with_token(
    user: User,
    days_remaining: int,
    token: str,
    custom_message: Optional[str] = None,
) -> bool:
    """
    Send a check-in reminder push notification with quick check-in token.

    Args:
        user: The user to remind.
        days_remaining: Days until check-in deadline.
        token: Session token for quick check-in.
        custom_message: Optional custom reminder message.

    Returns:
        bool: True if notification was sent successfully.
    """
    if not user.fcm_token:
        logger.info(f"User {user.id} has no FCM token, skipping reminder")
        return False

    push_data = get_reminder_push(days_remaining)

    # Use custom message if provided
    body = custom_message if custom_message else push_data["body"]

    # Deep link URL for quick check-in
    deep_link = f"solocheck://checkin?auto=true&token={token}"

    return send_push_notification(
        fcm_token=user.fcm_token,
        title=push_data["title"],
        body=body,
        data={
            "type": "checkin_reminder",
            "days_remaining": str(days_remaining),
            "token": token,
            "deep_link": deep_link,
            "action": "quick_checkin",
        },
    )


def send_sos_alert_email(
    db: Session,
    user: User,
    contact: "EmergencyContact",
    location_url: Optional[str] = None,
) -> bool:
    """
    Send an SOS emergency alert email to a contact.

    Args:
        db: Database session.
        user: The user who triggered SOS.
        contact: The emergency contact to notify.
        location_url: Optional Google Maps URL with user's location.

    Returns:
        bool: True if notification was sent successfully.
    """
    if contact.contact_type != "email":
        logger.info(f"Contact {contact.id} is not email type, skipping SOS alert")
        return False

    nickname = user.nickname or "사용자"
    contact_name = contact.name

    # Build location section
    location_section = ""
    if location_url:
        location_section = f"""
        <p style="margin-top: 20px;">
            <strong>마지막 위치:</strong><br/>
            <a href="{location_url}" style="color: #007AFF;">지도에서 보기</a>
        </p>
        """

    html_content = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #ff3b30; color: white; padding: 20px; border-radius: 12px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">SOS 긴급 알림</h1>
        </div>

        <div style="padding: 20px;">
            <p style="font-size: 16px;">{contact_name}님께,</p>

            <p style="font-size: 16px; line-height: 1.6;">
                <strong>{nickname}</strong>님이 SoloCheck 앱에서 <strong style="color: #ff3b30;">SOS 긴급 알림</strong>을 발송했습니다.
            </p>

            <p style="font-size: 16px; line-height: 1.6;">
                가능한 빨리 {nickname}님에게 연락을 시도해 주세요.
            </p>

            {location_section}

            <div style="margin-top: 30px; padding: 16px; background-color: #fff3cd; border-radius: 8px;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>주의:</strong> 이 알림은 의료적 판단이 아닌 긴급 연락 요청입니다.<br/>
                    긴급 상황이 의심되면 119에 연락해 주세요.
                </p>
            </div>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center; color: #666; font-size: 12px;">
            <p>SoloCheck - 1인 가구 안부 확인 서비스</p>
        </div>
    </body>
    </html>
    """

    success = send_email(
        to_email=contact.contact_value,
        subject=f"[SOS 긴급] {nickname}님의 긴급 알림",
        html_content=html_content,
    )

    # Log the notification
    log_notification(
        db=db,
        user_id=user.id,
        contact_id=contact.id,
        notification_type="sos_alert",
        status="sent" if success else "failed",
        error_message=None if success else "Failed to send SOS alert email",
    )

    return success


def send_urgent_reminder_with_token(
    user: User,
    token: str,
    custom_message: Optional[str] = None,
) -> bool:
    """
    Send an urgent check-in reminder push notification with quick check-in token.

    This is sent when the user is in the grace period.

    Args:
        user: The user to remind urgently.
        token: Session token for quick check-in.
        custom_message: Optional custom reminder message.

    Returns:
        bool: True if notification was sent successfully.
    """
    if not user.fcm_token:
        logger.info(f"User {user.id} has no FCM token, skipping urgent reminder")
        return False

    push_data = get_urgent_reminder_push()

    # Use custom message if provided (but keep urgent title)
    body = custom_message if custom_message else push_data["body"]

    # Deep link URL for quick check-in
    deep_link = f"solocheck://checkin?auto=true&token={token}"

    return send_push_notification(
        fcm_token=user.fcm_token,
        title=push_data["title"],
        body=body,
        data={
            "type": "urgent_reminder",
            "token": token,
            "deep_link": deep_link,
            "action": "quick_checkin",
        },
    )
