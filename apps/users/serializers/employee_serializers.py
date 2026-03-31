from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer
from apps.users.models import Employee
from rest_framework import serializers


class EmployeeSerializer(DynamicFieldsModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    branch_name = serializers.CharField(
        source="branch.name", read_only=True, allow_null=True
    )
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )
    designation_title = serializers.CharField(
        source="designation.title", read_only=True, allow_null=True
    )

    # Make some fields optional with defaults
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    date_of_exit = serializers.DateField(required=False, allow_null=True)
    probation_end_date = serializers.DateField(required=False, allow_null=True)
    confirmation_date = serializers.DateField(required=False, allow_null=True)
    emergency_contact_name = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    emergency_contact_phone = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    emergency_contact_relation = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    permanent_address = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    current_address = serializers.CharField(
        required=False, allow_blank=True, default=""
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "user_name",
            "employee_id",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "department",
            "department_name",
            "designation",
            "designation_title",
            "manager",
            "date_of_birth",
            "gender",
            "marital_status",
            "nationality",
            "personal_email",
            "phone_number",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
            "permanent_address",
            "current_address",
            "date_of_joining",
            "date_of_exit",
            "employment_status",
            "probation_end_date",
            "confirmation_date",
            "pan_number",
            "citizenship_number",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_name",
            "company_name",
            "branch_name",
            "department_name",
            "designation_title",
        ]

    def validate_user(self, value):
        # When updating, exclude the current instance from the check
        if self.instance:
            if (
                Employee.objects.filter(user=value)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Employee with this user already exists."
                )
        else:
            # When creating, check if user already has an employee profile
            if Employee.objects.filter(user=value).exists():
                raise serializers.ValidationError(
                    "Employee with this user already exists."
                )
        return value

    def create(self, validated_data):
        # Set default values for optional fields if not provided
        if "date_of_birth" not in validated_data or not validated_data["date_of_birth"]:
            from datetime import date

            validated_data["date_of_birth"] = date(2000, 1, 1)  # Default date
        if "emergency_contact_name" not in validated_data:
            validated_data["emergency_contact_name"] = "N/A"
        if "emergency_contact_phone" not in validated_data:
            validated_data["emergency_contact_phone"] = "N/A"
        if "emergency_contact_relation" not in validated_data:
            validated_data["emergency_contact_relation"] = "N/A"
        if "permanent_address" not in validated_data:
            validated_data["permanent_address"] = "N/A"
        if "current_address" not in validated_data:
            validated_data["current_address"] = "N/A"

        return super().create(validated_data)
