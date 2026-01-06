from rest_framework import serializers
from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer

class DesignationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        from apps.department.models import Designation
        model = Designation
        fields = [
            'id',
            'company',
            'title',
            'department',
            'code',
            'description',
            'level',
            'is_active'
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Designation title cannot be empty.")
        return value