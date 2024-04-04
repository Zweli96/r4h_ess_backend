from django.db import models
from django.contrib.auth.models import User

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
    lead = models.OneToOneField(User, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)


class District(models.Model):
    class Regions(models.TextChoices):
        NORTHERN_REGION = "Northern Region", "Northern Region"
        SOUTHERN_REGION = "Southern Region", "Southern Region"
        CENTRAL_REGION = "Central Region", "Central Region"

    name = models.CharField(max_length=200)
    region = models.CharField(choices=Regions, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)
    optimization_district = models.BooleanField(default=False)


class Staff(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'

    class Staff_Types(models.TextChoices):
        DIRECTORS = 'Directors', 'Directors'
        MANAGERS = 'Managers', 'Managers'
        SUPPORT_STAFF = 'Support Staff', 'Support Staff'
        COURIERS = 'Couriers', 'Couriers'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=200, null=False, blank=False)
    sex = models.CharField(choices=Gender, max_length=10,
                           null=False, blank=False)
    line_manager = manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True)
    projects = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True)
    staff_type = models.CharField(choices=Staff_Types, max_length=50,
                                  null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)
