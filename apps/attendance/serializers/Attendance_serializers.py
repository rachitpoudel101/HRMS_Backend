from rest_framework import serializers
from apps.attendance.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model with approval fields and work duration
    """

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)
    approved_by_name = serializers.CharField(
        source="approved_by.username", read_only=True
    )
    work_duration = serializers.SerializerMethodField()
    work_duration_hours = serializers.SerializerMethodField()
    work_duration_minutes = serializers.SerializerMethodField()
    total_hours = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id",
            "check_in",
            "check_out",
            "date",
            "status",
            "work_duration",
            "work_duration_hours",
            "work_duration_minutes",
            "total_hours",
            "is_approved",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_approved",
            "approved_by",
            "approved_at",
        ]

    def get_work_duration(self, obj):
        """
        Calculate work duration in human readable format (e.g., '8 hours 30 minutes')
        """
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours} hours {minutes} minutes"
        return None

    def get_work_duration_hours(self, obj):
        """
        Get only hours worked
        """
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
            return duration.seconds // 3600
        return 0

    def get_work_duration_minutes(self, obj):
        """
        Get remaining minutes after hours
        """
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
            return (duration.seconds % 3600) // 60
        return 0

    def get_total_hours(self, obj):
        """
        Get total hours as decimal (e.g., 8.5 for 8 hours 30 minutes)
        """
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
            total_seconds = duration.total_seconds()
            return round(total_seconds / 3600, 2)
        return 0.0


class AttendanceListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing attendance records with work duration
    """

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)
    work_duration = serializers.SerializerMethodField()
    total_hours = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id",
            "date",
            "check_in",
            "check_out",
            "status",
            "work_duration",
            "total_hours",
            "is_approved",
        ]
        read_only_fields = ["id"]

    def get_work_duration(self, obj):
        """Calculate work duration in human readable format"""
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return None

    def get_total_hours(self, obj):
        """Get total hours as decimal"""
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
            total_seconds = duration.total_seconds()
            return round(total_seconds / 3600, 2)
        return 0.0


class AttendanceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating attendance records (admin/HR only)
    """

    class Meta:
        model = Attendance
        fields = [
            "employee",
            "check_in",
            "check_out",
            "date",
            "status",
        ]

    def validate(self, data):
        """
        Validate that check_out is after check_in
        """
        if data.get("check_in") and data.get("check_out"):
            if data["check_out"] <= data["check_in"]:
                raise serializers.ValidationError(
                    "Check-out time must be after check-in time"
                )
        return data


class AttendanceApprovalSerializer(serializers.ModelSerializer):
    """
    Serializer for manager to approve attendance records
    """

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id",
            "date",
            "check_in",
            "check_out",
            "status",
            "is_approved",
            "approved_by",
            "approved_at",
        ]
        read_only_fields = [
            "id",
            "employee",
            "date",
            "check_in",
            "check_out",
            "status",
            "approved_by",
            "approved_at",
        ]
