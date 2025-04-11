from django.db import models
from django.contrib.auth.models import User
# from timesheets.models import Project
from timesheets.models import Activity
# Create your models here.
STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("DELETED", "DELETED"),
)

DISTRICT_REGIONS = (
    ("Northern Region", "Northern Region"),
    ("Southern Region", "Southern Region"),
    ("Central Region", "Central Region"),
)


class Department(models.Model):
    name = models.CharField(max_length=50)
    lead = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="led_depts", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, on_delete=models.SET_NULL, related_name='created_depts', null=True
    )
    edited_at = models.DateField(auto_now=True)
    status = models.CharField(
        max_length=200, choices=STATUS, null=True, default="ACTIVE")

    def __str__(self):
        return self.name


class District(models.Model):
    class Regions(models.TextChoices):
        NORTHERN_REGION = "Northern Region", "Northern Region"
        SOUTHERN_REGION = "Southern Region", "Southern Region"
        CENTRAL_REGION = "Central Region", "Central Region"

    name = models.CharField(max_length=200)
    # region = models.CharField(choices=Regions, max_length=200)
    region = models.CharField(choices=Regions.choices, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True, null=True)
    status = models.CharField(
        max_length=200, choices=STATUS, null=True, default="ACTIVE")

    def __str__(self):
        return self.name


class Staff(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'

    class StaffTypes(models.TextChoices):
        DIRECTORS = 'Directors', 'Directors'
        MANAGERS = 'Managers', 'Managers'
        SUPPORT_STAFF = 'Support Staff', 'Support Staff'
        COURIERS = 'Couriers', 'Couriers'

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='staff_profile', null=False)
    position = models.CharField(max_length=200, null=False, blank=False)
    # sex = models.CharField(choices=Gender, max_length=10,
    #                        null=True, blank=True)
    sex = models.CharField(choices=Gender.choices, max_length=10, null=True, blank=True)
    line_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_staff")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_district")
    # projects = models.ManyToManyField(
    #     Project, related_name="staff_projects", blank=True)
    project_activities = models.ManyToManyField(
        Activity, related_name="staff_activity_projects", blank=True)
    staff_type = models.CharField(choices=StaffTypes, max_length=50,
                                  null=True, blank=True),
    hr_approval = models.BooleanField(default=False)
    employee_number = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL, related_query_name='created_staff'
    )
    edited_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=200, choices=STATUS,  null=True, blank=True, default="ACTIVE")

    def __str__(self):
        return f'{self.user.first_name}_{self.user.last_name}_{self.district}'



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the Staff instance first
        if not self.project_activities.exists():  # Only add activities if none are already set
            # Add all available activities to the ManyToManyField
            self.project_activities.add(*Activity.objects.all())