"""
Celery tasks for SoloCheck.

This module defines the background tasks for checking missed check-ins
and sending notifications to users and their emergency contacts.
"""
import logging
from datetime import datetime, timedelta, timezone

from celery import shared_task
from sqlalchemy import and_

from src.checkin.service import generate_session_token
from src.common.encryption import decrypt_message
from src.database import SessionLocal
from src.notifications.service import (
    send_checkin_reminder,
    send_checkin_reminder_with_token,
    send_personal_message_alert,
    send_status_alert,
    send_urgent_reminder,
    send_urgent_reminder_with_token,
)
from src.contacts.service import get_active_contacts
from src.settings.service import (
    get_reminder_settings,
    is_in_quiet_hours,
    should_send_reminder,
)
from src.sos.service import is_sos_still_active, mark_sos_sent, get_sos_event
from src.users.models import User

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_missed_checkins(self) -> dict:
    """
    Check for users who have missed their check-in deadline.

    This task runs twice daily (at 00:00 and 12:00 UTC) and:
    1. Finds users whose last check-in + cycle + grace period has expired
    2. Sends status alerts to their emergency contacts
    3. Sends personal messages if enabled and available

    Returns:
        dict: Summary of processed users and notifications sent.
    """
    logger.info("Starting check_missed_checkins task")

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # Find active users with a last_check_in time
        users = db.query(User).filter(
            and_(
                User.is_active == True,  # noqa: E712
                User.last_check_in.isnot(None),
            )
        ).all()

        processed = 0
        alerts_sent = 0
        messages_sent = 0

        for user in users:
            # Calculate the deadline (last_check_in + cycle days + grace period hours)
            deadline = (
                user.last_check_in
                + timedelta(days=user.check_in_cycle)
                + timedelta(hours=user.grace_period)
            )

            # Check if the deadline has passed
            if now > deadline:
                logger.info(f"User {user.id} has missed their check-in deadline")
                processed += 1

                # Calculate days since last check-in
                days_since = (now - user.last_check_in).days

                # Send status alerts to all approved (consented) contacts only
                active_contacts = get_active_contacts(db, user.id)
                for contact in active_contacts:
                    success = send_status_alert(
                        db=db,
                        user=user,
                        contact=contact,
                        days_since_checkin=days_since,
                    )
                    if success:
                        alerts_sent += 1

                    # Send personal message if enabled
                    if (
                        user.personal_message
                        and user.personal_message.is_enabled
                        and user.personal_message.content
                    ):
                        try:
                            decrypted_message = decrypt_message(
                                user.personal_message.content
                            )
                            success = send_personal_message_alert(
                                db=db,
                                user=user,
                                contact=contact,
                                message=decrypted_message,
                            )
                            if success:
                                messages_sent += 1
                        except Exception as e:
                            logger.error(
                                f"Failed to decrypt/send message for user {user.id}: {e}"
                            )

        result = {
            "processed_users": processed,
            "alerts_sent": alerts_sent,
            "messages_sent": messages_sent,
            "timestamp": now.isoformat(),
        }

        logger.info(f"check_missed_checkins completed: {result}")
        return result

    except Exception as e:
        logger.error(f"check_missed_checkins task failed: {e}")
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_alert_to_contacts(self, user_id: str) -> dict:
    """
    Send alert notifications to all emergency contacts of a specific user.

    This can be triggered manually or by other tasks when immediate
    notification is needed.

    Args:
        user_id: The ID of the user whose contacts should be notified.

    Returns:
        dict: Summary of notifications sent.
    """
    logger.info(f"Starting send_alert_to_contacts for user {user_id}")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"User {user_id} not found")
            return {"error": "User not found"}

        if not user.last_check_in:
            logger.warning(f"User {user_id} has no check-in history")
            return {"error": "No check-in history"}

        now = datetime.now(timezone.utc)
        days_since = (now - user.last_check_in).days

        alerts_sent = 0
        messages_sent = 0

        # Send only to approved (consented) contacts
        active_contacts = get_active_contacts(db, user.id)
        for contact in active_contacts:
            # Send status alert
            success = send_status_alert(
                db=db,
                user=user,
                contact=contact,
                days_since_checkin=days_since,
            )
            if success:
                alerts_sent += 1

            # Send personal message if available
            if (
                user.personal_message
                and user.personal_message.is_enabled
                and user.personal_message.content
            ):
                try:
                    decrypted_message = decrypt_message(
                        user.personal_message.content
                    )
                    success = send_personal_message_alert(
                        db=db,
                        user=user,
                        contact=contact,
                        message=decrypted_message,
                    )
                    if success:
                        messages_sent += 1
                except Exception as e:
                    logger.error(f"Failed to send personal message: {e}")

        result = {
            "user_id": user_id,
            "alerts_sent": alerts_sent,
            "messages_sent": messages_sent,
            "timestamp": now.isoformat(),
        }

        logger.info(f"send_alert_to_contacts completed: {result}")
        return result

    except Exception as e:
        logger.error(f"send_alert_to_contacts task failed: {e}")
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_reminder_notifications(self) -> dict:
    """
    Send check-in reminder push notifications to users.

    This task runs every 6 hours and sends reminders to users whose
    check-in deadline is approaching, respecting user's reminder settings:
    - Customizable reminder hours (default: 48, 24, 12 hours before)
    - Quiet hours respect
    - Custom messages
    - Session token for quick check-in

    Returns:
        dict: Summary of reminders sent.
    """
    logger.info("Starting send_reminder_notifications task")

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # Find active users with FCM token and last_check_in
        users = db.query(User).filter(
            and_(
                User.is_active == True,  # noqa: E712
                User.fcm_token.isnot(None),
                User.last_check_in.isnot(None),
            )
        ).all()

        normal_sent = 0
        urgent_sent = 0
        skipped_quiet = 0

        for user in users:
            # Get user's reminder settings
            reminder_settings = get_reminder_settings(db, user.id)

            # Skip if push notifications are disabled
            if reminder_settings and not reminder_settings.push_enabled:
                continue

            # Check quiet hours
            if reminder_settings and is_in_quiet_hours(reminder_settings):
                skipped_quiet += 1
                continue

            # Calculate deadline (check-in cycle without grace period)
            cycle_deadline = user.last_check_in + timedelta(days=user.check_in_cycle)

            # Calculate full deadline (with grace period)
            full_deadline = cycle_deadline + timedelta(hours=user.grace_period)

            # Calculate hours until deadline
            hours_until_deadline = int((cycle_deadline - now).total_seconds() / 3600)

            # Check if user is in grace period (cycle passed but full deadline not)
            if now > cycle_deadline and now < full_deadline:
                # Generate session token for quick check-in
                session_token = generate_session_token(db, user.id)
                if session_token:
                    # Send urgent reminder with token
                    custom_message = (
                        reminder_settings.custom_message
                        if reminder_settings
                        else None
                    )
                    success = send_urgent_reminder_with_token(
                        user,
                        session_token.token,
                        custom_message,
                    )
                else:
                    # Fallback to regular urgent reminder
                    success = send_urgent_reminder(user)

                if success:
                    urgent_sent += 1
                    logger.info(f"Sent urgent reminder to user {user.id}")
            elif hours_until_deadline > 0:
                # Check if we should send based on user's reminder settings
                should_send, custom_message = should_send_reminder(
                    db, user, hours_until_deadline
                )

                if should_send:
                    # Generate session token for quick check-in
                    session_token = generate_session_token(db, user.id)
                    days_remaining = hours_until_deadline // 24

                    if session_token:
                        # Send reminder with token
                        success = send_checkin_reminder_with_token(
                            user,
                            days_remaining,
                            session_token.token,
                            custom_message,
                        )
                    else:
                        # Fallback to regular reminder
                        success = send_checkin_reminder(user, days_remaining)

                    if success:
                        normal_sent += 1
                        logger.info(
                            f"Sent reminder to user {user.id}: "
                            f"{hours_until_deadline} hours remaining"
                        )

        result = {
            "normal_reminders_sent": normal_sent,
            "urgent_reminders_sent": urgent_sent,
            "skipped_quiet_hours": skipped_quiet,
            "timestamp": now.isoformat(),
        }

        logger.info(f"send_reminder_notifications completed: {result}")
        return result

    except Exception as e:
        logger.error(f"send_reminder_notifications task failed: {e}")
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_expired_session_tokens(self) -> dict:
    """
    Clean up expired session tokens.

    This task runs daily to remove expired or used session tokens
    from the database.

    Returns:
        dict: Summary of tokens cleaned up.
    """
    logger.info("Starting cleanup_expired_session_tokens task")

    db = SessionLocal()
    try:
        from src.checkin.service import cleanup_expired_tokens

        deleted = cleanup_expired_tokens(db)

        result = {
            "tokens_deleted": deleted,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"cleanup_expired_session_tokens completed: {result}")
        return result

    except Exception as e:
        logger.error(f"cleanup_expired_session_tokens task failed: {e}")
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sos_alerts_delayed(self, sos_event_id: str) -> dict:
    """
    Send SOS alerts to emergency contacts after countdown delay.

    This task is scheduled with a delay when SOS is triggered.
    If the SOS is cancelled before this runs, no alerts are sent.

    Args:
        sos_event_id: The SOS event identifier.

    Returns:
        dict: Summary of alerts sent.
    """
    logger.info(f"Starting send_sos_alerts_delayed for SOS {sos_event_id}")

    db = SessionLocal()
    try:
        # Check if SOS is still active (not cancelled)
        if not is_sos_still_active(db, sos_event_id):
            logger.info(f"SOS {sos_event_id} was cancelled, skipping alerts")
            return {
                "sos_event_id": sos_event_id,
                "status": "cancelled",
                "alerts_sent": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Get the SOS event and user
        sos_event = get_sos_event(db, sos_event_id)
        if sos_event is None:
            logger.warning(f"SOS event {sos_event_id} not found")
            return {"error": "SOS event not found"}

        user = sos_event.user
        if not user:
            logger.warning(f"User for SOS {sos_event_id} not found")
            return {"error": "User not found"}

        # Get approved emergency contacts
        active_contacts = get_active_contacts(db, user.id)

        alerts_sent = 0
        now = datetime.now(timezone.utc)

        # Build location string if available
        location_str = None
        if sos_event.location_lat and sos_event.location_lng:
            location_str = f"https://maps.google.com/maps?q={sos_event.location_lat},{sos_event.location_lng}"

        # Send alerts to each contact
        for contact in active_contacts:
            if contact.contact_type == "email":
                try:
                    from src.notifications.service import send_sos_alert_email

                    success = send_sos_alert_email(
                        db=db,
                        user=user,
                        contact=contact,
                        location_url=location_str,
                    )
                    if success:
                        alerts_sent += 1
                except Exception as e:
                    logger.error(f"Failed to send SOS alert to {contact.id}: {e}")

        # Mark SOS as sent
        mark_sos_sent(db, sos_event_id)

        result = {
            "sos_event_id": sos_event_id,
            "status": "sent",
            "alerts_sent": alerts_sent,
            "timestamp": now.isoformat(),
        }

        logger.info(f"send_sos_alerts_delayed completed: {result}")
        return result

    except Exception as e:
        logger.error(f"send_sos_alerts_delayed task failed: {e}")
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()
