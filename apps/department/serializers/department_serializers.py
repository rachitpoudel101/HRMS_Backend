from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer
from apps.department.models import Department
from rest_framework import serializers

class DepartmentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Department
        fields = [
            'id',
            'company',
            'name',
            'branch',
            'code',
            'description',
            'parent_department',
            'is_active'
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department name cannot be empty.")
        return value
    