from apps.users.models import User
from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer,BaseAuditSerializer
from rest_framework import serializers

class UserSerializer(DynamicFieldsModelSerializer,BaseAuditSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'role',
            'company',
            'is_active',
            'last_login',
        ]
        read_only_fields = ['id', 'company', 'last_login', 'created_by', 'updated_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user