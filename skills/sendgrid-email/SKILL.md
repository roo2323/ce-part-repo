---
name: sendgrid-email
description: SendGrid 이메일 발송 시 사용. SCHEDULER 전용. 이메일 API 연동.
---

# SendGrid 이메일 발송 체크리스트

## 파일 구조
- [ ] `src/notifications/email.py` - 이메일 유틸리티
- [ ] `src/notifications/templates.py` - 이메일 템플릿

## SendGrid 설정
- [ ] API 키 환경변수
- [ ] 발신자 이메일 설정
- [ ] 발신자 이름 설정

## 이메일 구성
- [ ] from_email
- [ ] to_emails
- [ ] subject
- [ ] html_content

## 필수 고지 문구 (SoloCheck)
- [ ] "본 서비스는 사망 여부를 확인하지 않습니다"
- [ ] "긴급 상황 시 112/119 등 공공기관에 연락하세요"

---

## email.py 템플릿
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from src.config import settings


def send_via_sendgrid(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str
) -> dict:
    """SendGrid로 이메일 발송
    
    Args:
        to_email: 수신자 이메일
        to_name: 수신자 이름
        subject: 제목
        html_content: HTML 본문
        
    Returns:
        dict: 발송 결과
    """
    message = Mail(
        from_email=Email(settings.SENDGRID_FROM_EMAIL, "SoloCheck"),
        to_emails=To(to_email, to_name),
        subject=subject,
        html_content=Content("text/html", html_content)
    )
    
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(message)
    
    return {
        "status_code": response.status_code,
        "success": response.status_code in [200, 201, 202],
    }
```

## templates.py 템플릿
```python
def get_status_alert_template(
    user_nickname: str,
    contact_name: str,
    days_missed: int,
    personal_message: str = None
) -> tuple[str, str]:
    """상태 알림 이메일 템플릿
    
    Returns:
        tuple[str, str]: (제목, HTML 본문)
    """
    subject = f"[SoloCheck] {user_nickname}님의 안부 확인 알림"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4F46E5; color: white; padding: 20px; }}
            .content {{ padding: 20px; background: #f9fafb; }}
            .message {{ background: white; padding: 15px; border-left: 4px solid #4F46E5; margin: 15px 0; }}
            .footer {{ padding: 20px; font-size: 12px; color: #6b7280; }}
            .warning {{ background: #fef3c7; padding: 10px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>안부 확인 알림</h1>
            </div>
            <div class="content">
                <p>{contact_name}님, 안녕하세요.</p>
                <p><strong>{user_nickname}</strong>님이 <strong>{days_missed}일</strong> 동안 
                안부 확인을 하지 않았습니다.</p>
                
                {"<div class='message'><p><strong>개인 메시지:</strong></p><p>" + personal_message + "</p></div>" if personal_message else ""}
                
                <div class="warning">
                    <p><strong>⚠️ 중요 안내</strong></p>
                    <ul>
                        <li>본 서비스는 사망 여부를 확인하지 않습니다.</li>
                        <li>긴급 상황 시 112/119 등 공공기관에 연락하세요.</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>본 메일은 {user_nickname}님이 SoloCheck 서비스에 등록한 비상연락처로 발송되었습니다.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content
```

## 태스크에서 사용
```python
@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def send_status_alert_email(
    self,
    contact_email: str,
    contact_name: str,
    user_nickname: str,
    days_missed: int,
    personal_message: str = None
):
    """상태 알림 이메일 발송"""
    subject, html_content = get_status_alert_template(
        user_nickname, contact_name, days_missed, personal_message
    )
    
    result = send_via_sendgrid(contact_email, contact_name, subject, html_content)
    return result
```

---

## 완료 확인
- [ ] SendGrid 연동 구현
- [ ] 이메일 템플릿 작성
- [ ] 필수 고지 문구 포함
- [ ] 태스크 연동
