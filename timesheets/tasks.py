from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Period, Timesheet
from datetime import datetime, timedelta
from staff.models import Staff
from django.template.loader import render_to_string
from django.conf import settings


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


timesheet_data = {
    'submission_date': '2023-10-01',
    'period': 'October 2023',
    'hours_worked': 160,
    'leave_days': 2
}


@shared_task
def send_timesheet_approval_notification(line_manager_email="zgolowa@r4hmw.org", line_manager_name="Zwelithini Golowa", staff_name="Richard Nyali", timesheet_data=timesheet_data):
    try:
        print(
            f"Processing approval notification email for {staff_name} - {timesheet_data['period']}...")
        subject = f"Timesheet Submission by {staff_name} awaiting review"
        # Adjust URL as needed
        review_url = f"{settings.SYSTEM_URL}/approvals"

        # Context for the email template
        context = {
            'line_manager_name': line_manager_name,
            'staff_name': staff_name,
            'submission_date': timesheet_data['submission_date'],
            'period': timesheet_data['period'],
            'hours_worked': timesheet_data['hours_worked'],
            'leave_days': timesheet_data['leave_days'],
            'review_url': review_url,
        }

        # Render the HTML template
        html_message = render_to_string(
            'timesheet_approval_notification_email.html', context)

        # Send the email
        send_mail(
            subject=subject,
            message="A new timesheet has been submitted.",  # Plain text fallback
            from_email=f"R4H TIMESHEETS <{settings.DEFAULT_FROM_EMAIL}>",
            recipient_list=[line_manager_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(e)
