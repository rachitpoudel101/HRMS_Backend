from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer
from apps.users.models import Company
from rest_framework import serializers

class CompanySerializer(DynamicFieldsModelSerializer):
    name = serializers.CharField(max_length=200,required=True)
    code = serializers.CharField(max_length=50,required=True)
    registration_number = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'code',
            'registration_number',
            'address',
            'city',
            'country',
            'phone',
            'email',
            'website',
            'logo',
            'is_active',
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']
        
        def validate_code(self, value):
            if Company.objects.filter(code=value).exists():
                raise serializers.ValidationError("Company code must be unique.")
            return value
        def validate_email(self, value):
            if Company.objects.filter(email=value).exists():
                raise serializers.ValidationError("Company email must be unique.")
            return value