from datetime import timedelta

from app.config.celery import celery_app
from app.utils.utils import send_email
from app.models.reminder import Reminder


# TODO: implement `get_task_by_id` utility function for including task name in reminder email
#   + implement make_date_humanic for transfeting datetime to readable date format
@celery_app.task
def schedule_reminder(reminder: Reminder):
    body = f"""
Hey, here is your deadline reminder for following task: ...
Deadline of your task is comming soon: {reminder.reminder_time}

Your message: {reminder.message}
    """
    # default time for sending reminders is 3 hours before the deadline
    reminder_time = reminder.reminder_time - timedelta(hours=3)

    send_email(reminder.user_email, "WazowskiList: deadline reminder", body).apply_async(
        args=[reminder.user_email, "Your WazowskiList reminder", body],
        eta=reminder_time
    )
