from apps.common.mixins.baseSerilizerMixins import (
    DynamicFieldsModelSerializer,
    BaseAuditSerializer,
)
from apps.users.models import Branch, Company
from rest_framework import serializers


class CompanyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name"]


class BranchSerializer(DynamicFieldsModelSerializer, BaseAuditSerializer):
    company = CompanyNameSerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), write_only=True, required=True
    )

    class Meta:
        model = Branch
        fields = [
            "id",
            "company",
            "company_id",
            "name",
            "code",
            "address",
            "city",
            "phone",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        company = validated_data.pop("company_id")
        validated_data["company"] = company
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "company_id" in validated_data:
            company = validated_data.pop("company_id")
            validated_data["company"] = company
        return super().update(instance, validated_data)

    def validate_code(self, value):
        if (
            Branch.objects.filter(code=value)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                "Branch code must be unique within the company."
            )
        return value

    def validate_name(self, value):
        if (
            Branch.objects.filter(name=value)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                "Branch name must be unique within the company."
            )
        return value
