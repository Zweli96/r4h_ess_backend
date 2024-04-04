from django.db import models
from staff.models import Staff
from django.contrib.auth.models import User


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
    status = models.CharField(max_length=200, choices=STATUS, null=True)


class Period(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    total_days = models.IntegerField()
    deadline = models.DateField()
    public_holidays = models.ManyToManyField(PublicHoliday, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(max_length=200, choices=STATUS, null=True)


class Project(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)


class Timesheet(models.Model):
    class Current_Status(models.TextChoices):
        SUBMITTED = "Submitted", "Submitted"
        LINE_APPROVED = "Line Manager Approved", "Line Manager Approved"
        HR_APPROVED = "HR Approved", "HR Approved"
        REJECTED = "Central Region", "Central Region"

    period = models.ForeignKey(
        Period, on_delete=models.SET_NULL, null=True)
    projects = models.ManyToManyField(Project)
    current_status = models.CharField(choices=Current_Status, max_length=20,
                                      null=False, blank=False)
    first_approver = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True)
    first_approval_date = models.DateField()
    second_approver = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True)
    second_approval_date = models.DateField()
    rejected_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True)
    rejected_date = models.DateField()
    comment = models.CharField(max_length=200, null=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    leave_days = models.IntegerField()
    working_days = models.IntegerField()
    filled_timesheet = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(max_length=200, choices=STATUS, null=True)
