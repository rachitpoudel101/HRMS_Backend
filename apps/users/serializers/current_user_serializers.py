from rest_framework import serializers
from apps.users.models import User, Employee


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serializer for current authenticated user with complete profile including employee details
    """

    # User basic info
    full_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(
        source="company.name", read_only=True, allow_null=True
    )
    company_id = serializers.IntegerField(
        source="company.id", read_only=True, allow_null=True
    )

    # Employee profile info (if exists)
    employee_id = serializers.SerializerMethodField()
    employee_profile_id = serializers.SerializerMethodField()
    branch_id = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    department_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    designation_id = serializers.SerializerMethodField()
    designation_title = serializers.SerializerMethodField()
    employment_status = serializers.SerializerMethodField()
    date_of_joining = serializers.SerializerMethodField()
    manager_id = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    personal_email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "role",
            "company_id",
            "company_name",
            "is_active",
            "is_super",
            "last_login",
            # Employee profile fields
            "employee_profile_id",
            "employee_id",
            "branch_id",
            "branch_name",
            "department_id",
            "department_name",
            "designation_id",
            "designation_title",
            "employment_status",
            "date_of_joining",
            "manager_id",
            "manager_name",
            "phone_number",
            "personal_email",
        ]

    def get_full_name(self, obj):
        """Return full name or username if names not set"""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username

    def get_employee_profile_id(self, obj):
        """Return employee profile ID if exists"""
        try:
            return obj.employee_profile.id
        except Employee.DoesNotExist:
            return None

    def get_employee_id(self, obj):
        """Return employee ID if profile exists"""
        try:
            return obj.employee_profile.employee_id
        except Employee.DoesNotExist:
            return None

    def get_branch_id(self, obj):
        """Return branch ID if employee profile exists"""
        try:
            return (
                obj.employee_profile.branch.id if obj.employee_profile.branch else None
            )
        except Employee.DoesNotExist:
            return None

    def get_branch_name(self, obj):
        """Return branch name if employee profile exists"""
        try:
            return (
                obj.employee_profile.branch.name
                if obj.employee_profile.branch
                else None
            )
        except Employee.DoesNotExist:
            return None

    def get_department_id(self, obj):
        """Return department ID if employee profile exists"""
        try:
            return (
                obj.employee_profile.department.id
                if obj.employee_profile.department
                else None
            )
        except Employee.DoesNotExist:
            return None

    def get_department_name(self, obj):
        """Return department name if employee profile exists"""
        try:
            return (
                obj.employee_profile.department.name
                if obj.employee_profile.department
                else None
            )
        except Employee.DoesNotExist:
            return None

    def get_designation_id(self, obj):
        """Return designation ID if employee profile exists"""
        try:
            return (
                obj.employee_profile.designation.id
                if obj.employee_profile.designation
                else None
            )
        except Employee.DoesNotExist:
            return None

    def get_designation_title(self, obj):
        """Return designation title if employee profile exists"""
        try:
            return (
                obj.employee_profile.designation.title
                if obj.employee_profile.designation
                else None
            )
        except Employee.DoesNotExist:
            return None

    def get_employment_status(self, obj):
        """Return employment status if employee profile exists"""
        try:
            return obj.employee_profile.employment_status
        except Employee.DoesNotExist:
            return None

    def get_date_of_joining(self, obj):
        """Return date of joining if employee profile exists"""
        try:
            return obj.employee_profile.date_of_joining
        except Employee.DoesNotExist:
            return None

    def get_manager_id(self, obj):
        """Return manager's employee ID if exists"""
        try:
            return (
                obj.employee_profile.manager.id
                if obj.employee_profile.manager
                else None
            )
        except (Employee.DoesNotExist, AttributeError):
            return None

    def get_manager_name(self, obj):
        """Return manager's name if exists"""
        try:
            if obj.employee_profile.manager:
                return (
                    obj.employee_profile.manager.user.get_full_name()
                    or obj.employee_profile.manager.user.username
                )
            return None
        except (Employee.DoesNotExist, AttributeError):
            return None

    def get_phone_number(self, obj):
        """Return phone number from employee profile"""
        try:
            return obj.employee_profile.phone_number
        except Employee.DoesNotExist:
            return None

    def get_personal_email(self, obj):
        """Return personal email from employee profile"""
        try:
            return obj.employee_profile.personal_email
        except Employee.DoesNotExist:
            return None
