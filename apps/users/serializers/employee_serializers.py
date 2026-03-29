from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer, BaseAuditSerializer
from apps.users.models import Employee
from rest_framework import serializers

class EmployeeSerializer(DynamicFieldsModelSerializer, BaseAuditSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'employee_id',
            'company',
            'branch',
            'department',
            'designation',
            'manager',
            'date_of_birth',
            'gender',
            'marital_status',
            'nationality',
            'personal_email',
            'phone_number',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relation',
            'permanent_address',
            'current_address',
            'date_of_joining',
            'date_of_exit',
            'employment_status',
            'probation_end_date',
            'confirmation_date',
            'pan_number',
            'citizenship_number', 
        ]
        read_only_fields = ['id', 'company', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def validate_user(self, value):
        if Employee.objects.filter(user=value).exists():
            raise serializers.ValidationError("Employee with this user already exists.")
        return value
