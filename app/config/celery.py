from celery import Celery
from app.config.settings import settings

# Redis as the broker
celery_app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.scheduler"]
)

celery_app.conf.timezone = 'UTC'
celery_app.conf.enable_utc = True
