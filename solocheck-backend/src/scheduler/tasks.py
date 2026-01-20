"""
Celery tasks for SoloCheck.

This module defines the background tasks for checking missed check-ins
and sending notifications to users and their emergency contacts.
"""
import logging
from datetime import datetime, timedelta, timezone

from celery import shared_task
from sqlalchemy import and_

from src.common.encryption import decrypt_message
from src.database import SessionLocal
from src.notifications.service import (
    send_checkin_reminder,
    send_personal_message_alert,
    send_status_alert,
    send_urgent_reminder,
)
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

                # Send status alerts to all emergency contacts
                for contact in user.emergency_contacts:
                    if contact.is_verified:
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

        for contact in user.emergency_contacts:
            if contact.is_verified:
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
    check-in deadline is approaching:
    - Normal reminder: 3, 2, 1 days before deadline
    - Urgent reminder: In grace period (deadline passed but not yet expired)

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

        for user in users:
            # Calculate deadline (check-in cycle without grace period)
            cycle_deadline = user.last_check_in + timedelta(days=user.check_in_cycle)

            # Calculate full deadline (with grace period)
            full_deadline = cycle_deadline + timedelta(hours=user.grace_period)

            days_remaining = (cycle_deadline - now).days

            # Check if user is in grace period (cycle passed but full deadline not)
            if now > cycle_deadline and now < full_deadline:
                # Send urgent reminder
                success = send_urgent_reminder(user)
                if success:
                    urgent_sent += 1
                    logger.info(f"Sent urgent reminder to user {user.id}")
            elif 0 <= days_remaining <= 3:
                # Send normal reminder (within 3 days of deadline)
                success = send_checkin_reminder(user, days_remaining)
                if success:
                    normal_sent += 1
                    logger.info(
                        f"Sent reminder to user {user.id}: {days_remaining} days remaining"
                    )

        result = {
            "normal_reminders_sent": normal_sent,
            "urgent_reminders_sent": urgent_sent,
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
