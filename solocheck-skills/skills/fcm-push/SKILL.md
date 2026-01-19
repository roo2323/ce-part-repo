---
name: fcm-push
description: Firebase Cloud Messaging 푸시 알림 발송 시 사용. SCHEDULER 전용. FCM 연동.
---

# FCM 푸시 알림 체크리스트

## 파일 구조
- [ ] `src/notifications/fcm.py` - FCM 유틸리티
- [ ] Firebase 서비스 계정 JSON 파일

## Firebase 초기화
- [ ] `firebase_admin` 패키지 사용
- [ ] 서비스 계정 인증
- [ ] 앱 시작 시 1회 초기화

## 메시지 구성
- [ ] `notification`: 제목, 본문
- [ ] `data`: 추가 데이터 (선택)
- [ ] `android`: Android 설정
- [ ] `apns`: iOS 설정

## 에러 처리
- [ ] `UnregisteredError`: 토큰 무효
- [ ] 기타 에러: 재시도

---

## fcm.py 템플릿
```python
import firebase_admin
from firebase_admin import credentials, messaging
from src.config import settings

_firebase_app = None


def init_firebase():
    """Firebase 초기화 (1회)"""
    global _firebase_app
    if not _firebase_app:
        cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


class InvalidTokenError(Exception):
    """FCM 토큰 무효 예외"""
    pass


def send_fcm_message(
    token: str,
    title: str,
    body: str,
    data: dict = None,
    badge: int = None
) -> str:
    """FCM 푸시 메시지 발송
    
    Args:
        token: FCM 디바이스 토큰
        title: 알림 제목
        body: 알림 본문
        data: 추가 데이터 (선택)
        badge: iOS 배지 숫자 (선택)
        
    Returns:
        str: 메시지 ID
        
    Raises:
        InvalidTokenError: 토큰이 유효하지 않음
    """
    init_firebase()
    
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=token,
        
        # Android 설정
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                sound="default",
                priority="high",
                channel_id="solocheck_alerts",
            ),
        ),
        
        # iOS 설정
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default",
                    badge=badge,
                    content_available=True,
                ),
            ),
            headers={
                "apns-priority": "10",
                "apns-push-type": "alert",
            },
        ),
    )
    
    try:
        response = messaging.send(message)
        return response
    except messaging.UnregisteredError:
        raise InvalidTokenError(f"Token unregistered: {token[:20]}...")
```

## 태스크에서 사용
```python
from src.notifications.fcm import send_fcm_message, InvalidTokenError


@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def send_push_notification(self, fcm_token: str, title: str, body: str, data: dict = None):
    """푸시 알림 발송 태스크"""
    try:
        message_id = send_fcm_message(fcm_token, title, body, data)
        logger.info(f"Push sent: {message_id}")
        return {"success": True, "message_id": message_id}
        
    except InvalidTokenError:
        # 토큰 무효화 처리 (재시도 없음)
        invalidate_fcm_token(fcm_token)
        return {"success": False, "error": "invalid_token"}
```

---

## 완료 확인
- [ ] Firebase 초기화 구현
- [ ] 메시지 구성 완료
- [ ] Android/iOS 설정
- [ ] 에러 처리 (토큰 무효)
- [ ] 태스크 연동
