import csv
import random
from django.contrib.auth.models import User


def generate_passwords(output_csv='user_passwords.csv'):
    # Fetch all users
    users = User.objects.all()
    success_count = 0
    error_count = 0

    # Open CSV file to write usernames and passwords
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'password'])  # CSV header

        for user in users:
            try:
                # Use last_name if available, else fallback to username
                base_name = user.last_name if user.last_name else user.username
                # Ensure base_name is not empty; use 'User' as fallback
                base_name = base_name if base_name else 'User'
                # Generate random 3-digit number
                random_digits = f"{random.randint(0, 999):03d}"
                # Create password in format Lastname@[random 3 digits]@2025
                password = f"{base_name}@{random_digits}@2025"

                # Set the new password for the user in Django
                user.set_password(password)
                user.save()

                # Write to CSV
                writer.writerow([user.username, password])
                success_count += 1
                print(f"Updated password for user: {user.username}")

            except Exception as e:
                print(
                    f"Error updating password for user {user.username}: {str(e)}")
                error_count += 1

    print(
        f"Password generation complete. Successfully updated {success_count} users. Failed: {error_count}")
    print(f"Passwords saved to {output_csv}")


if __name__ == "__main__":
    generate_passwords()
