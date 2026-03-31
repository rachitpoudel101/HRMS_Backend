from rest_framework import serializers
from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer
from apps.department.models import Designation


class DesignationSerializer(DynamicFieldsModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Designation
        fields = [
            "id",
            "company",
            "company_name",
            "title",
            "department",
            "department_name",
            "code",
            "description",
            "level",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "company_name",
            "department_name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Designation title cannot be empty.")
        return value
