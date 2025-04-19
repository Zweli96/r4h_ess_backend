from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from .tasks import send_timesheet_approval_notification


# Create your models here.

STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("DELETED", "DELETED"),
)


class PublicHoliday(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=200, choices=STATUS, null=True, default="ACTIVE")

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField(max_length=50, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_hours = models.DecimalField(
        max_digits=5, decimal_places=2, editable=False)
    total_days = models.IntegerField(editable=False)
    deadline = models.DateField()
    public_holidays = models.ManyToManyField(PublicHoliday, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=200, choices=STATUS, null=True, default="ACTIVE")

    def __str__(self):
        return self.name

    @staticmethod
    def calculate_business_days(start_date, end_date):
        if not start_date or not end_date:
            return 0

        total_days = (end_date - start_date).days + 1
        business_days = 0

        for day in range(total_days):
            current_day = start_date + timedelta(days=day)
            # Monday is 0 and Sunday is 6
            if current_day.weekday() < 5:  # Monday to Friday are business days
                business_days += 1

        return business_days

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.total_days = (self.end_date - self.start_date).days
            self.total_hours = self.calculate_business_days(
                self.start_date, self.end_date) * 8
        super().save(*args, **kwargs)


# class Project(models.Model):
#     name = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(
#         User, blank=True, null=True, on_delete=models.SET_NULL
#     )
#     edited_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(
#         max_length=200, choices=STATUS, null=True, default="ACTIVE")

    def __str__(self):
        return self.name


class Timesheet(models.Model):
    class Current_Status(models.TextChoices):
        SUBMITTED = "Submitted", "Submitted"
        LINE_APPROVED = "Line Manager Approved", "Line Manager Approved"
        HR_APPROVED = "HR Approved", "HR Approved"
        REJECTED = "Rejected", "Rejected"

    period = models.CharField(max_length=255, null=True)
    current_status = models.CharField(choices=Current_Status.choices, max_length=50,
                                      null=False, blank=False)
    current_status = models.CharField(choices=Current_Status, max_length=50,
                                      null=False, blank=False)
    line_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="line_manager_timesheets")
    first_approver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="first_approved_timesheets")
    first_approval_date = models.DateTimeField(null=True, blank=True)
    second_approver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="second_approved_timesheets", blank=True)
    second_approval_date = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="rejected_timesheets", blank=True)
    rejected_date = models.DateTimeField(null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    leave_days = models.IntegerField()
    working_days = models.IntegerField()
    filled_timesheet = models.JSONField(null=True)
    edited_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=200, choices=STATUS, null=True, default="ACTIVE")

    def __str__(self):
        return f'{self.period}_{self.created_by.first_name}_{self.created_by.last_name}'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:  # Only send request for approval for the creation of new time
            timesheet_data = {
                'id': self.id,  # Fix: Quote the key
                # Convert DateTime to string
                'submission_date': self.created_at.strftime('%Y-%m-%d'),
                'period': self.period,
                # Convert Decimal to string
                'hours_worked': str(self.total_hours),
                'leave_days': self.leave_days,
            }

            send_timesheet_approval_notification.delay(
                line_manager_email=self.line_manager.email,
                line_manager_name=f"{self.line_manager.first_name} {self.line_manager.last_name}",
                staff_name=f"{self.created_by.first_name} {self.created_by.last_name}",
                timesheet_data=timesheet_data,
            )

 # activity model


class Activity(models.Model):
    TYPE_CHOICES = (
        ('PROJECT', 'Project'),
        ('LEAVE', 'Leave'),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=200, choices=STATUS, null=True, default="ACTIVE")
    is_loe = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_activities')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='modified_activities', null=True, blank=True)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
