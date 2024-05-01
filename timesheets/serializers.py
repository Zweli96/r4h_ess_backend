# todo/todo_api/serializers.py
from rest_framework import serializers
from .models import Timesheet


class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = ["period", "current_status", "first_approver", "first_approval_date", "second_approver", "second_approval_date",
                  "rejected_by", "rejected_date", "comment", "total_hours", "leave_days", "working_days", "filled_timesheet", "created_at", "created_by", "status", "edited_at"]
