from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer, BaseAuditSerializer
from apps.users.models import Branch
from rest_framework import serializers

class BranchSerializer(DynamicFieldsModelSerializer, BaseAuditSerializer):
    class Meta:
        model = Branch
        fields = [
            'id',
            'company',
            'name',
            'code',
            'address',
            'city',
            'phone',
            'is_active',
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']
        
        def validate_code(self, value):
            if Branch.objects.filter(code=value).exists():
                raise serializers.ValidationError("Branch code must be unique within the company.")
            return value
        def validate_name(self, value):
            if Branch.objects.filter(name=value).exists():
                raise serializers.ValidationError("Branch name must be unique within the company.")
            return value
        