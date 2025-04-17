# todo/todo_api/serializers.py
# from rest_framework import serializers
# from .models import Timesheet, Period
from staff.models import Staff,District


from rest_framework import views, serializers, response
from .models import Timesheet, Period,Activity
from rest_framework.views import APIView

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff  # Replace with your Staff model
        fields = ["first_name", "last_name"]


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ["id", "name", "start_date", "end_date", "total_hours", "total_days",
                  "deadline", "public_holidays", "created_at", "created_by", "status"]


class TimesheetSerializer(serializers.ModelSerializer):
    created_by_full_name = serializers.SerializerMethodField()
    # period_name = serializers.SerializerMethodField()

    class Meta:
        model = Timesheet
        fields = ["id", "period", "current_status", "first_approver", "first_approval_date", "second_approver", "second_approval_date",
                 "rejected_by", "rejected_date", "comment", "total_hours", "leave_days", "working_days", "filled_timesheet", "created_by_full_name", "created_at", "created_by", "status", "edited_at", "line_manager"]

    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    # def get_period_name(self, obj):
    #     if obj.period:
    #         return obj.period.name
    #     return None



class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class ActivityListApiView(APIView):
    def get(self, request):
        activities = Activity.objects.all()
        serializer = ActivitySerializer(activities, many=True)
        return response.Response(serializer.data)



class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']


class TimesheetReportSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    staff_name = serializers.CharField()
    department = serializers.CharField()
    district = serializers.CharField()
    period = serializers.CharField()
    project = serializers.DictField()
    total_work_hours = serializers.FloatField()
    total_leave_hours = serializers.FloatField()
    total_available_hours = serializers.FloatField()
    LOE = serializers.FloatField()