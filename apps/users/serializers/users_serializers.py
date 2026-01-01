from apps.users.models import User
from apps.common.mixins.baseSerilizerMixins import DynamicFieldsModelSerializer,BaseAuditSerializer

class UserSerializer(DynamicFieldsModelSerializer,BaseAuditSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'company',
            'is_active',
            'last_login',
        ]
        read_only_fields = ['id', 'last_login', 'created_by', 'updated_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user