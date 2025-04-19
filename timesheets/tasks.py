from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
from django.template.loader import render_to_string
from django.conf import settings

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


@shared_task
def send_timesheet_due_reminder(staff_email, staff_name, period):
    print(
        f"Processing timesheet due reminder email for {staff_name} - {period}...")
    try:
        subject = f"Timesheet Due Reminder for {period}"
        # Adjust URL as needed
        submit_url = f"{settings.SYSTEM_URL}/timesheets"

        context = {
            'staff_name': staff_name,
            'period': period,
            'submit_url': submit_url,
        }

        html_message = render_to_string(
            'timesheet_due_email.html', context)

        send_mail(
            subject=subject,
            # Plain text fallback
            message=f"Hello {staff_name}, the timesheet for {period} is due today.",
            from_email=f"R4H TIMESHEETS <{settings.DEFAULT_FROM_EMAIL}>",
            recipient_list=[staff_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(e)


@shared_task
def send_timesheet_due_reminders_to_all():
    # Fetch all active users (adjust query as needed)
    period = datetime.now().strftime("%B %Y")
    users = User.objects.filter(is_active=True)
    for user in users:
        if user.email:  # Ensure user has an email
            send_timesheet_due_reminder.delay(
                staff_email=user.email,
                staff_name=f"{user.first_name} {user.last_name}",
                period=period
            )
