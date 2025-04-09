from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Period, Timesheet
from datetime import datetime, timedelta
from staff.models import Staff


# Function to send email to remind users to submit their timesheets
@shared_task
# def send_email():
def send_timesheet_reminder_email():
    try:
        print("Processing reminder emails...")
        # Get the the period that is due
        today = datetime.now().date()
        # due_period = Period.objects.filter(
        #     end_date=today - timedelta(days=1)).first()

        due_period = Period.objects.filter(id=1).first()

        # users = User.objects.all()
        users = User.objects.select_related(
            "staff_profile").filter(staff_profile__department_id=1)

        for user in users:
            email_body = f"""
                        Hello {user.first_name} {user.last_name},

                        Timesheet for {due_period.name} is due. Please log in to the system and submit your timesheet.

                        Login here: {settings.SYSTEM_URL}
                    """
            print(f"Sending email to {user.email}")
            send_mail(f"{due_period.name} Timesheet Reminder",
                      email_body,
                      "R4H TIMESHEETS <zgolowa@r4hmw.org>",
                      [user.email],
                      fail_silently=False)
        return f"emails sent to {len(users)} users"
    except Exception as e:
        print(e)
