# fastapi
from fastapi import HTTPException, status
# models
from app.models.user import User
from app.models.reminder import Reminder
# utility
from app.utils.utils import get_task_by_id, make_date_humanitic
# db
from motor.motor_asyncio import AsyncIOMotorDatabase
# sending emails
import smtplib
from email.mime.text import MIMEText
# settings
from app.config.settings import settings
# celery config
from app.config.celery import celery_app
# other modules
import uuid
from asyncio import run


# TODO: re-write adding, updating and deleting logic with `aioredis`.
#   basically, connection logic will be the same like with MongoDB

@celery_app.task
def schedule_reminder(
        reminder: Reminder,
        task_id: uuid.UUID,
        current_user: User,
        db: AsyncIOMotorDatabase
):
    """Celery task for sending reminder email

    Args:
        reminder (Reminder): reminder pydantic model
        task_id (UUID): ID of the task
        current_user (User): Pydantic model of the user performing task
        db (AsyncIOMotorDatabase): The database connection instance

    Raises:
        smtplib.SMTPException: if reminder email cannot be sent

    """
    # this part may be tricky, but I needed to use asyncio.run
    # for calling an original `async` function as `sync` one.
    # Because Celery doesn't support calling `async` functions
    # (or it may support and I just didn't know that)
    msg = run(prepare_email_body(reminder, task_id, current_user, db))

    msg['From'] = settings.SMTP_USER
    msg['Subject'] = "Your reminder email from WazowskiList"
    msg['To'] = reminder.user_email

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, reminder.user_email, msg.as_string())
    except smtplib.SMTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {e}"
        )


async def prepare_email_body(
        reminder: Reminder,
        task_id: uuid.UUID,
        current_user: User,
        db: AsyncIOMotorDatabase
) -> MIMEText:
    task = await get_task_by_id(task_id, current_user, db)
    body = f"""
    Hey, your deadline is coming soon for the following task: {task}
    Deadline time: {make_date_humanitic(reminder.reminder_time)}

    Your reminding message: {reminder.message}
    """
    return MIMEText(body)
