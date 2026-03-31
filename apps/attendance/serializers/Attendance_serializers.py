from rest_framework import serializers
from apps.attendance.models import Attendance, FingerprintScan


class FingerprintScanSerializer(serializers.ModelSerializer):
    """
    Serializer for FingerprintScan model
    """

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)

    class Meta:
        model = FingerprintScan
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id",
            "scan_time",
            "scan_type",
            "device_id",
            "scan_status",
            "attendance",
        ]
        read_only_fields = ["id", "scan_time"]


class FingerprintScanListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing fingerprint scans
    """

    class Meta:
        model = FingerprintScan
        fields = ["id", "scan_time", "scan_type", "scan_status", "device_id"]
        read_only_fields = ["id", "scan_time"]


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model
    """

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)
    check_in_scan_details = FingerprintScanListSerializer(
        source="check_in_scan", read_only=True
    )
    check_out_scan_details = FingerprintScanListSerializer(
        source="check_out_scan", read_only=True
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
            "check_in_scan",
            "check_out_scan",
            "check_in_scan_details",
            "check_out_scan_details",
            "date",
            "status",
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


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
        ]
        read_only_fields = ["id"]


class AttendanceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating attendance records
    """

    class Meta:
        model = Attendance
        fields = [
            "employee",
            "check_in",
            "check_out",
            "check_in_scan",
            "check_out_scan",
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
