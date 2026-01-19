---
name: celery-task
description: Celery 태스크 구현 시 사용. SCHEDULER 전용. 배치 작업 및 재시도 로직.
---

# Celery 태스크 구현 체크리스트

## 태스크 데코레이터
- [ ] `@shared_task` 사용
- [ ] `bind=True` (self 접근 필요 시)
- [ ] `name` 명시적 지정

## 재시도 설정
- [ ] `max_retries`: 최대 재시도 횟수
- [ ] `autoretry_for`: 자동 재시도 예외
- [ ] `retry_backoff`: 지수 백오프
- [ ] `retry_backoff_max`: 최대 대기 시간

## 제한 시간
- [ ] `soft_time_limit`: 경고 (초)
- [ ] `time_limit`: 강제 종료 (초)

## 로깅
- [ ] `get_task_logger(__name__)` 사용
- [ ] 시작/완료/에러 로그

## DB 세션
- [ ] `SessionLocal()` 직접 생성
- [ ] `try/finally`로 세션 종료

---

## 태스크 템플릿
```python
from celery import shared_task
from celery.utils.log import get_task_logger
from src.database import SessionLocal

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    name="src.scheduler.tasks.{task_name}",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    soft_time_limit=30,
    time_limit=60,
)
def {task_name}(self, param1: str, param2: str):
    """태스크 설명
    
    Args:
        param1: 파라미터 설명
        param2: 파라미터 설명
        
    Returns:
        dict: 처리 결과
    """
    logger.info(f"Starting {task_name}: {param1}")
    
    db = SessionLocal()
    try:
        # 비즈니스 로직
        result = do_something(db, param1, param2)
        
        logger.info(f"Completed {task_name}: {result}")
        return {"success": True, "result": result}
        
    except SpecificError as e:
        # 특정 에러는 재시도 없이 실패
        logger.warning(f"Specific error, not retrying: {e}")
        return {"success": False, "error": str(e)}
        
    except Exception as e:
        logger.error(f"Failed {task_name}: {e}")
        raise  # 자동 재시도 트리거
        
    finally:
        db.close()
```

## 수동 재시도 예시
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, to_email: str, subject: str, body: str):
    try:
        result = sendgrid_send(to_email, subject, body)
        return {"success": True}
        
    except RateLimitError as e:
        # Rate Limit - 5분 후 재시도
        raise self.retry(exc=e, countdown=300)
        
    except Exception as e:
        # 기본 간격으로 재시도
        raise self.retry(exc=e)
```

## 미체크 감지 태스크 예시
```python
@shared_task(bind=True, name="src.scheduler.tasks.check_missed_checkins")
def check_missed_checkins(self):
    """미체크 사용자 감지 및 알림 트리거"""
    logger.info("Starting missed check-in detection")
    
    db = SessionLocal()
    try:
        # 미체크 대상자 조회
        query = text("""
            SELECT u.id, u.nickname
            FROM users u
            WHERE u.is_active = true
              AND u.last_check_in IS NOT NULL
              AND u.last_check_in + INTERVAL '1 day' * u.check_in_cycle 
                  + INTERVAL '1 hour' * u.grace_period < NOW()
        """)
        
        missed_users = db.execute(query).fetchall()
        logger.info(f"Found {len(missed_users)} missed users")
        
        # 각 사용자에 대해 알림 발송 큐잉
        for user in missed_users:
            send_alert_to_contacts.delay(user.id)
        
        return {"processed": len(missed_users)}
        
    finally:
        db.close()
```

---

## 완료 확인
- [ ] 태스크 데코레이터 설정
- [ ] 재시도 로직 구현
- [ ] 로깅 적용
- [ ] DB 세션 관리
- [ ] 에러 처리
