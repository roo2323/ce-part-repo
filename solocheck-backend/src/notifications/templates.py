"""
Notification templates for 하루안부.

This module provides email and push notification templates with
required legal disclaimers as specified in CLAUDE.md.
"""
from typing import Optional


# Legal disclaimer (required by CLAUDE.md Section 7)
LEGAL_DISCLAIMER = """
---
본 서비스는 사망 여부를 확인하지 않습니다.
긴급 상황 시 112/119 등 공공기관에 연락하세요.
이 알림은 '연락 두절' 기준으로 발송됩니다.
"""

LEGAL_DISCLAIMER_HTML = """
<hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
<p style="color: #666; font-size: 12px; line-height: 1.6;">
본 서비스는 사망 여부를 확인하지 않습니다.<br>
긴급 상황 시 112/119 등 공공기관에 연락하세요.<br>
이 알림은 '연락 두절' 기준으로 발송됩니다.
</p>
"""


def get_status_alert_email(
    nickname: str,
    contact_name: str,
    days: int,
) -> dict:
    """
    Generate status alert email template.

    This email is sent to emergency contacts when a user has not checked in
    for the specified period.

    Args:
        nickname: The user's display name.
        contact_name: The recipient's name.
        days: Number of days since last check-in.

    Returns:
        dict: Contains 'subject' and 'html' keys.
    """
    user_display = nickname or "하루안부 사용자"

    subject = f"[하루안부] {user_display}님의 연락 두절 알림"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>하루안부 알림</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background-color: #f5f5f5;">
    <div style="background-color: #ffffff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #007AFF; font-size: 24px; margin: 0;">하루안부</h1>
        </div>

        <p style="color: #333; font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            안녕하세요 {contact_name}님,
        </p>

        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 16px; margin: 24px 0; border-radius: 4px;">
            <p style="color: #856404; font-size: 16px; margin: 0;">
                <strong>{user_display}</strong>님이 <strong>{days}일</strong> 동안 체크인하지 않았습니다.
            </p>
        </div>

        <p style="color: #333; font-size: 14px; line-height: 1.6;">
            {user_display}님이 귀하를 비상연락처로 등록했습니다.
            연락을 시도해주시거나, 직접 확인해주시면 감사하겠습니다.
        </p>

        {LEGAL_DISCLAIMER_HTML}
    </div>
</body>
</html>
"""

    return {"subject": subject, "html": html}


def get_personal_message_email(
    nickname: str,
    contact_name: str,
    message: str,
) -> dict:
    """
    Generate personal message email template.

    This email is sent to emergency contacts with the user's personal message
    after the grace period has expired.

    Args:
        nickname: The user's display name.
        contact_name: The recipient's name.
        message: The user's personal message.

    Returns:
        dict: Contains 'subject' and 'html' keys.
    """
    user_display = nickname or "하루안부 사용자"

    subject = f"[하루안부] {user_display}님이 남긴 메시지입니다"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>하루안부 개인 메시지</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background-color: #f5f5f5;">
    <div style="background-color: #ffffff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #007AFF; font-size: 24px; margin: 0;">하루안부</h1>
        </div>

        <p style="color: #333; font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            안녕하세요 {contact_name}님,
        </p>

        <p style="color: #333; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">
            {user_display}님이 미리 작성해 둔 메시지를 전달드립니다.
        </p>

        <div style="background-color: #f8f9fa; border-radius: 8px; padding: 24px; margin: 24px 0;">
            <p style="color: #333; font-size: 16px; line-height: 1.8; margin: 0; white-space: pre-wrap;">
{message}
            </p>
        </div>

        <p style="color: #666; font-size: 12px; margin-top: 24px;">
            이 메시지는 법적 효력이 없으며, 단순 안부 전달 목적으로만 사용됩니다.
        </p>

        {LEGAL_DISCLAIMER_HTML}
    </div>
</body>
</html>
"""

    return {"subject": subject, "html": html}


def get_reminder_push(days_remaining: int) -> dict:
    """
    Generate check-in reminder push notification.

    Args:
        days_remaining: Number of days until the check-in deadline.

    Returns:
        dict: Contains 'title' and 'body' keys.
    """
    if days_remaining > 1:
        title = "체크인 리마인더"
        body = f"체크인 마감까지 {days_remaining}일 남았습니다. 앱을 열어 체크인해주세요."
    elif days_remaining == 1:
        title = "체크인 리마인더"
        body = "체크인 마감이 내일입니다. 잊지 말고 체크인해주세요!"
    else:
        title = "체크인 필요"
        body = "오늘 체크인 마감일입니다. 지금 바로 체크인해주세요."

    return {"title": title, "body": body}


def get_urgent_reminder_push() -> dict:
    """
    Generate urgent check-in reminder push notification.

    This is sent when the user is in the grace period and hasn't checked in.

    Returns:
        dict: Contains 'title' and 'body' keys.
    """
    return {
        "title": "긴급: 체크인이 필요합니다",
        "body": "체크인 기한이 지났습니다. 비상연락처에 알림이 발송되기 전에 체크인해주세요.",
    }


def get_contact_registration_email(
    user_nickname: str,
    contact_name: str,
) -> dict:
    """
    Generate contact registration notification email.

    This email is sent when a user registers someone as an emergency contact.

    Args:
        user_nickname: The user's display name.
        contact_name: The contact's name.

    Returns:
        dict: Contains 'subject' and 'html' keys.
    """
    user_display = user_nickname or "하루안부 사용자"

    subject = f"[하루안부] {user_display}님이 비상연락처로 등록했습니다"

    # Required disclaimer from CLAUDE.md Section 7.2
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>하루안부 알림</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background-color: #f5f5f5;">
    <div style="background-color: #ffffff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #007AFF; font-size: 24px; margin: 0;">하루안부</h1>
        </div>

        <p style="color: #333; font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            안녕하세요 {contact_name}님,
        </p>

        <p style="color: #333; font-size: 14px; line-height: 1.6;">
            <strong>{user_display}</strong>님이 귀하를 비상연락처로 등록했습니다.
        </p>

        <p style="color: #333; font-size: 14px; line-height: 1.6;">
            이 서비스는 일정 기간 체크인이 없을 경우 알림을 보내드립니다.
        </p>

        <div style="background-color: #e8f4ff; border-radius: 8px; padding: 16px; margin: 24px 0;">
            <p style="color: #0066cc; font-size: 14px; margin: 0; line-height: 1.6;">
                본 알림은 의료적 판단이 아닌 연락 두절 상태만을 알립니다.
            </p>
        </div>

        {LEGAL_DISCLAIMER_HTML}
    </div>
</body>
</html>
"""

    return {"subject": subject, "html": html}
