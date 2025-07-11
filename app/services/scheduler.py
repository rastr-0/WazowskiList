# sending emails
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# settings
from app.config.settings import settings
# celery config
from app.config.celery import celery_app
# logs
from app.logs.logging_config import reminder_logger


@celery_app.task(name="schedule_reminder")
def schedule_reminder(
        user_email: str,
        body_text: str
):
    """Celery task for sending emails"""
    reminder_logger.info("Start of the schedule_reminder task")
    msg = MIMEMultipart("alternative")

    msg['From'] = settings.SMTP_USER
    msg["Subject"] = "🔔 Reminder: Task deadline is coming!"
    msg['To'] = user_email
    msg.attach(MIMEText(body_text, "html"))
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, str(user_email), msg.as_string())
        reminder_logger.info(f"Reminder was successfully to: {user_email}")
    except smtplib.SMTPException as _:
        reminder_logger.error(f"Error sending email to: {user_email}")
        raise smtplib.SMTPException
