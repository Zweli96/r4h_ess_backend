from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    district = serializers.StringRelatedField(source='district.name')
    department = serializers.StringRelatedField(source='department.name')
    line_manager = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['district', 'line_manager', 'department',
                  'employee_number', 'hr_approval', 'status', 'position']

    def get_line_manager(self, obj):
        if obj.line_manager:
            return f"{obj.line_manager.first_name} {obj.line_manager.last_name}".strip()
        return None


class CustomUserSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(source='staff_profile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email', 'staff']

    def get_staff(self, obj):
        try:
            staff = obj.staff  # or obj.staff_set.first() if no related_name
            return StaffSerializer(staff).data
        except Staff.DoesNotExist:
            return None
