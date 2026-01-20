"""
Tests for the Celery scheduler tasks and notification service.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.common.encryption import encrypt_message
from src.contacts.models import EmergencyContact
from src.messages.models import PersonalMessage
from src.notifications.models import NotificationLog
from src.notifications.templates import (
    get_personal_message_email,
    get_reminder_push,
    get_status_alert_email,
    get_urgent_reminder_push,
)
from src.scheduler.tasks import (
    check_missed_checkins,
    send_alert_to_contacts,
    send_reminder_notifications,
)
from src.users.models import User


class TestNotificationTemplates:
    """Tests for notification email and push templates."""

    def test_status_alert_email_template(self):
        """Test status alert email generation."""
        result = get_status_alert_email(
            nickname="홍길동",
            contact_name="김철수",
            days=7,
        )

        assert "subject" in result
        assert "html" in result
        assert "홍길동" in result["subject"]
        assert "홍길동" in result["html"]
        assert "김철수" in result["html"]
        assert "7일" in result["html"]
        # Check legal disclaimer
        assert "사망 여부를 확인하지 않습니다" in result["html"]

    def test_status_alert_email_with_no_nickname(self):
        """Test status alert email when nickname is not provided."""
        result = get_status_alert_email(
            nickname="",
            contact_name="김철수",
            days=7,
        )

        assert "SoloCheck 사용자" in result["subject"]
        assert "SoloCheck 사용자" in result["html"]

    def test_personal_message_email_template(self):
        """Test personal message email generation."""
        result = get_personal_message_email(
            nickname="홍길동",
            contact_name="김철수",
            message="안녕하세요, 이 메시지를 받으셨다면...",
        )

        assert "subject" in result
        assert "html" in result
        assert "홍길동" in result["subject"]
        assert "안녕하세요, 이 메시지를 받으셨다면..." in result["html"]
        # Check legal disclaimer
        assert "법적 효력이 없으며" in result["html"]

    def test_reminder_push_3_days(self):
        """Test reminder push notification for 3 days remaining."""
        result = get_reminder_push(days_remaining=3)

        assert result["title"] == "체크인 리마인더"
        assert "3일" in result["body"]

    def test_reminder_push_1_day(self):
        """Test reminder push notification for 1 day remaining."""
        result = get_reminder_push(days_remaining=1)

        assert result["title"] == "체크인 리마인더"
        assert "내일" in result["body"]

    def test_reminder_push_0_days(self):
        """Test reminder push notification for deadline day."""
        result = get_reminder_push(days_remaining=0)

        assert result["title"] == "체크인 필요"
        assert "오늘" in result["body"]

    def test_urgent_reminder_push(self):
        """Test urgent reminder push notification."""
        result = get_urgent_reminder_push()

        assert "긴급" in result["title"]
        assert "비상연락처" in result["body"]


class TestCheckMissedCheckinsTask:
    """Tests for the check_missed_checkins Celery task."""

    @pytest.fixture
    def user_with_contact(self, db_session):
        """Create a test user with an emergency contact."""
        user = User(
            email="checkin_test@example.com",
            password_hash="hashed",
            nickname="체크인테스트",
            check_in_cycle=7,
            grace_period=48,
            is_active=True,
            # Check-in 10 days ago (should trigger alert with 7-day cycle + 48-hour grace)
            last_check_in=datetime.now(timezone.utc) - timedelta(days=10),
            fcm_token="test_fcm_token",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        contact = EmergencyContact(
            user_id=user.id,
            name="비상연락처",
            contact_type="email",
            contact_value="contact@example.com",
            is_verified=True,
        )
        db_session.add(contact)
        db_session.commit()

        return user

    @pytest.fixture
    def user_with_personal_message(self, user_with_contact, db_session):
        """Add a personal message to the test user."""
        message_content = encrypt_message("이 메시지는 테스트용입니다.")
        personal_message = PersonalMessage(
            user_id=user_with_contact.id,
            content=message_content,
            is_enabled=True,
        )
        db_session.add(personal_message)
        db_session.commit()

        return user_with_contact

    @patch("src.scheduler.tasks.SessionLocal")
    @patch("src.scheduler.tasks.send_status_alert")
    def test_check_missed_checkins_sends_alerts(
        self, mock_send_alert, mock_session, db_session, user_with_contact
    ):
        """Test that check_missed_checkins sends alerts for missed check-ins."""
        mock_session.return_value = db_session
        mock_send_alert.return_value = True

        result = check_missed_checkins()

        assert result["processed_users"] == 1
        assert mock_send_alert.called

    @patch("src.scheduler.tasks.SessionLocal")
    def test_check_missed_checkins_no_missed_users(self, mock_session, db_session):
        """Test check_missed_checkins with no missed users."""
        # Create user with recent check-in
        user = User(
            email="recent@example.com",
            password_hash="hashed",
            nickname="최근체크인",
            check_in_cycle=7,
            grace_period=48,
            is_active=True,
            last_check_in=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(user)
        db_session.commit()

        mock_session.return_value = db_session

        result = check_missed_checkins()

        assert result["processed_users"] == 0
        assert result["alerts_sent"] == 0


class TestSendReminderNotificationsTask:
    """Tests for the send_reminder_notifications Celery task."""

    @pytest.fixture
    def user_needs_reminder(self, db_session):
        """Create a user who needs a check-in reminder."""
        user = User(
            email="reminder_test@example.com",
            password_hash="hashed",
            nickname="리마인더테스트",
            check_in_cycle=7,
            grace_period=48,
            is_active=True,
            # Check-in 5 days ago (2 days until 7-day cycle deadline)
            last_check_in=datetime.now(timezone.utc) - timedelta(days=5),
            fcm_token="test_fcm_token",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user

    @patch("src.scheduler.tasks.SessionLocal")
    @patch("src.scheduler.tasks.send_checkin_reminder")
    def test_send_reminders_within_3_days(
        self, mock_send_reminder, mock_session, db_session, user_needs_reminder
    ):
        """Test that reminders are sent to users within 3 days of deadline."""
        mock_session.return_value = db_session
        mock_send_reminder.return_value = True

        result = send_reminder_notifications()

        assert result["normal_reminders_sent"] == 1
        assert mock_send_reminder.called

    @patch("src.scheduler.tasks.SessionLocal")
    @patch("src.scheduler.tasks.send_urgent_reminder")
    def test_send_urgent_reminder_in_grace_period(
        self, mock_urgent, mock_session, db_session
    ):
        """Test that urgent reminders are sent during grace period."""
        # Create user in grace period (cycle passed, grace not expired)
        user = User(
            email="grace_test@example.com",
            password_hash="hashed",
            nickname="유예기간테스트",
            check_in_cycle=7,
            grace_period=48,
            is_active=True,
            # Check-in 8 days ago (past 7-day cycle, in 48-hour grace)
            last_check_in=datetime.now(timezone.utc) - timedelta(days=8),
            fcm_token="test_fcm_token",
        )
        db_session.add(user)
        db_session.commit()

        mock_session.return_value = db_session
        mock_urgent.return_value = True

        result = send_reminder_notifications()

        assert result["urgent_reminders_sent"] == 1
        assert mock_urgent.called


class TestSendAlertToContactsTask:
    """Tests for the send_alert_to_contacts Celery task."""

    @pytest.fixture
    def user_for_manual_alert(self, db_session):
        """Create a user for manual alert testing."""
        user = User(
            email="manual_alert@example.com",
            password_hash="hashed",
            nickname="수동알림",
            check_in_cycle=7,
            grace_period=48,
            is_active=True,
            last_check_in=datetime.now(timezone.utc) - timedelta(days=10),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        contact = EmergencyContact(
            user_id=user.id,
            name="연락처",
            contact_type="email",
            contact_value="manual_contact@example.com",
            is_verified=True,
        )
        db_session.add(contact)
        db_session.commit()

        return user

    @patch("src.scheduler.tasks.SessionLocal")
    @patch("src.scheduler.tasks.send_status_alert")
    def test_send_alert_to_specific_user(
        self, mock_alert, mock_session, db_session, user_for_manual_alert
    ):
        """Test sending alerts to a specific user's contacts."""
        mock_session.return_value = db_session
        mock_alert.return_value = True

        result = send_alert_to_contacts(user_for_manual_alert.id)

        assert result["user_id"] == user_for_manual_alert.id
        assert mock_alert.called

    @patch("src.scheduler.tasks.SessionLocal")
    def test_send_alert_user_not_found(self, mock_session, db_session):
        """Test handling of non-existent user."""
        mock_session.return_value = db_session

        result = send_alert_to_contacts("non_existent_id")

        assert "error" in result
        assert result["error"] == "User not found"
