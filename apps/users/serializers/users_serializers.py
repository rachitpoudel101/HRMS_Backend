from apps.users.models import User, Company
from apps.common.mixins.baseSerilizerMixins import (
    DynamicFieldsModelSerializer,
    BaseAuditSerializer,
)
from rest_framework import serializers


class UserSerializer(DynamicFieldsModelSerializer, BaseAuditSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_name = serializers.CharField(source="company.name", read_only=True, allow_null=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=False,
        allow_null=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make company read-only for non-superadmin users
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'role') and user.role.upper() != 'SUPERADMIN':
                self.fields['company'].read_only = True

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "role",
            "company",
            "company_name",
            "is_active",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "company_name",
            "last_login",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        role = data.get("role", "").upper()
        company = data.get("company")
        request = self.context.get('request')

        # Superadmin cannot have a company
        if role == "SUPERADMIN" and company:
            raise serializers.ValidationError(
                {"role": "Superadmin users cannot be assigned to a company."}
            )

        # Only SUPERADMIN can specify company
        # For ADMIN/HR, company will be auto-set from their own company
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'role') and user.role.upper() != 'SUPERADMIN':
                if company and hasattr(user, 'company') and company != user.company:
                    raise serializers.ValidationError(
                        {"company": "You can only add users to your own company."}
                    )

        return data

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
