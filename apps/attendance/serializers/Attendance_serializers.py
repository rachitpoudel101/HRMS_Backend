from rest_framework import serializers
from apps.attendance.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model with approval fields
    """

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)
    approved_by_name = serializers.CharField(
        source="approved_by.username", read_only=True
    )

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


class AttendanceListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing attendance records
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
        ]
        read_only_fields = ["id"]


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
