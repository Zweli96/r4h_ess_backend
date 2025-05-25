import csv
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User


def send_credentials(csv_file='user_passwords.csv', login_url='http://98.97.162.222:8081/signin'):
    success_count = 0
    error_count = 0

    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['username']
            password = row['password']

            try:
                # Get user from Django User model
                user = User.objects.get(username=username)
                if not user.email:
                    print(f"No email found for user: {username}")
                    error_count += 1
                    continue

                # Get first name and last name, fallback to username if empty
                first_name = user.first_name if user.first_name else username
                last_name = user.last_name if user.last_name else ''
                full_name = f"{first_name} {last_name}".strip(
                ) if last_name else first_name

                # Render email template
                context = {
                    'username': username,
                    'password': password,
                    'login_url': login_url,
                    'full_name': full_name,
                }
                html_content = render_to_string(
                    'timesheet_credentials.html', context)
                text_content = f"""
Dear {full_name},

Your account for the Timesheet System has been created. Below are your login credentials:

Username: {username}
Password: {password}

Please log in to the Timesheet System at {login_url} and change your password after your first login.

This is an automated message from R4H ESS System.
"""
                # Send email
                email = EmailMultiAlternatives(
                    subject='Your Timesheet System Credentials',
                    body=text_content,
                    from_email=f"R4H TIMESHEETS <{settings.DEFAULT_FROM_EMAIL}>",
                    to=[user.email],
                )
                email.attach_alternative(html_content, 'text/html')
                email.send()

                success_count += 1
                print(f"Sent credentials to {username} at {user.email}")

            except User.DoesNotExist:
                print(f"User not found: {username}")
                error_count += 1
            except Exception as e:
                print(f"Error sending email to {username}: {str(e)}")
                error_count += 1

    print(
        f"Email sending complete. Successfully sent to {success_count} users. Failed: {error_count}")


if __name__ == "__main__":
    send_credentials()
