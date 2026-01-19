---
name: celery-config
description: Celery 앱 및 Beat 스케줄 설정 시 사용. SCHEDULER 전용. 워커 및 주기 작업 설정.
---

# Celery 설정 체크리스트

## 파일 구조
- [ ] `src/scheduler/celery_app.py` - Celery 앱 설정
- [ ] `src/scheduler/tasks.py` - 태스크 정의

## Celery 앱 설정
- [ ] broker (Redis URL)
- [ ] backend (Redis URL)
- [ ] include (태스크 모듈)
- [ ] timezone: UTC
- [ ] task_serializer: json

## 안정성 설정
- [ ] `task_acks_late = True`
- [ ] `task_reject_on_worker_lost = True`
- [ ] `worker_prefetch_multiplier = 1`

## Beat 스케줄
- [ ] 미체크 감지: 매일 00:00, 12:00
- [ ] 리마인더: 6시간마다
- [ ] 로그 정리: 매일 03:00

---

## celery_app.py 템플릿
```python
from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_app = Celery(
    "solocheck",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.scheduler.tasks"]
)

celery_app.conf.update(
    # 직렬화
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 시간대
    timezone="UTC",
    enable_utc=True,
    
    # 안정성
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    
    # 결과
    result_expires=3600,
)

# Beat 스케줄
celery_app.conf.beat_schedule = {
    # 미체크 감지 (매일 00:00, 12:00 UTC)
    "check-missed-checkins-midnight": {
        "task": "src.scheduler.tasks.check_missed_checkins",
        "schedule": crontab(hour=0, minute=0),
    },
    "check-missed-checkins-noon": {
        "task": "src.scheduler.tasks.check_missed_checkins",
        "schedule": crontab(hour=12, minute=0),
    },
    
    # 리마인더 발송 (6시간마다)
    "send-reminder-notifications": {
        "task": "src.scheduler.tasks.send_reminder_notifications",
        "schedule": crontab(hour="*/6", minute=0),
    },
    
    # 오래된 로그 정리 (매일 03:00 UTC)
    "cleanup-old-logs": {
        "task": "src.scheduler.tasks.cleanup_old_logs",
        "schedule": crontab(hour=3, minute=0),
    },
}
```

## 실행 명령어
```bash
# 워커 실행
celery -A src.scheduler.celery_app worker --loglevel=info

# Beat 스케줄러 실행
celery -A src.scheduler.celery_app beat --loglevel=info

# 개발: 워커 + Beat 동시
celery -A src.scheduler.celery_app worker --beat --loglevel=info
```

---

## 완료 확인
- [ ] Celery 앱 설정 완료
- [ ] Beat 스케줄 설정 완료
- [ ] Redis 연결 확인
- [ ] Docker Compose 설정
