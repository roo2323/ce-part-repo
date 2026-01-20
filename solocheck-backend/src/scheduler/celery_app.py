"""
Celery app configuration for SoloCheck.

This module sets up the Celery application with Redis as the broker/backend
and defines the beat schedule for periodic tasks.
"""
from celery import Celery
from celery.schedules import crontab

from src.config import settings

# Create Celery app instance
celery_app = Celery(
    "solocheck",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.scheduler.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Check for missed check-ins at midnight and noon UTC
    "check-missed-checkins-midnight": {
        "task": "src.scheduler.tasks.check_missed_checkins",
        "schedule": crontab(hour=0, minute=0),  # 00:00 UTC
        "options": {"queue": "default"},
    },
    "check-missed-checkins-noon": {
        "task": "src.scheduler.tasks.check_missed_checkins",
        "schedule": crontab(hour=12, minute=0),  # 12:00 UTC
        "options": {"queue": "default"},
    },
    # Send reminder notifications every 6 hours
    "send-reminder-notifications": {
        "task": "src.scheduler.tasks.send_reminder_notifications",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
        "options": {"queue": "default"},
    },
}
