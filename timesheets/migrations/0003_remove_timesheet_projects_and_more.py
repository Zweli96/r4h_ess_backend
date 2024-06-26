# Generated by Django 5.0.3 on 2024-04-09 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheets', '0002_period_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timesheet',
            name='projects',
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='first_approval_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='rejected_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='second_approval_date',
            field=models.DateField(null=True),
        ),
    ]
