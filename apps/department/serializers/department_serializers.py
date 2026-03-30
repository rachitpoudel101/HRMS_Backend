from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer
from apps.department.models import Department
from rest_framework import serializers

class DepartmentSerializer(DynamicFieldsModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Department
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'branch',
            'branch_name',
            'code',
            'description',
            'parent_department',
            'is_active'
        ]
        read_only_fields = ['id', 'company', 'company_name', 'branch_name', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department name cannot be empty.")
        return value