# Generated by Django 5.0.3 on 2024-12-29 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0010_staff_hr_approval'),
        ('timesheets', '0009_timesheet_department_approver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='staff_projects', to='timesheets.project'),
        ),
    ]
