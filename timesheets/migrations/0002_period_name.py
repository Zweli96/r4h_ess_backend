# Generated by Django 5.0.3 on 2024-04-09 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]