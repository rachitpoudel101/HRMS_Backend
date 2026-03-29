from rest_framework import serializers
from apps.notice.models import Notic, NoticeType, NoticeAttachment
from apps.users.serializers.employee_serializers import EmployeeSerializer
from apps.users.serializers.Branch_serializers import BranchSerializer


class NoticeTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for NoticeType model
    """
    class Meta:
        model = NoticeType
        fields = [
            'id',
            'type_name',
            'description',
            'created_at',
            'updated_at',
            'deleted_at',
            'created_by',
            'updated_by',
            'deleted_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoticeTypeListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing notice types
    """
    class Meta:
        model = NoticeType
        fields = ['id', 'type_name', 'description']
        read_only_fields = ['id']


class NoticeAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for NoticeAttachment model
    """
    class Meta:
        model = NoticeAttachment
        fields = [
            'id',
            'notice',
            'file',
            'description',
            'created_at',
            'updated_at',
            'deleted_at',
            'created_by',
            'updated_by',
            'deleted_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoticeAttachmentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing notice attachments
    """
    class Meta:
        model = NoticeAttachment
        fields = ['id', 'file', 'description']
        read_only_fields = ['id']


class NoticSerializer(serializers.ModelSerializer):
    """
    Serializer for Notic model
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    employees_details = EmployeeSerializer(source='employees', many=True, read_only=True)
    attachments_details = NoticeAttachmentListSerializer(source='attachments', many=True, read_only=True)
    
    class Meta:
        model = Notic
        fields = [
            'id',
            'name',
            'date',
            'description',
            'branch',
            'branch_name',
            'employees',
            'employees_details',
            'attachments_details',
            'created_at',
            'updated_at',
            'deleted_at',
            'created_by',
            'updated_by',
            'deleted_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoticListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing notices
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Notic
        fields = ['id', 'name', 'date', 'branch_name', 'employee_count', 'attachment_count']
        read_only_fields = ['id']
    
    def get_employee_count(self, obj):
        return obj.employees.count()
    
    def get_attachment_count(self, obj):
        return obj.attachments.count()


class NoticCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating notices
    """
    class Meta:
        model = Notic
        fields = [
            'id',
            'name',
            'date',
            'description',
            'branch',
            'employees'
        ]
        read_only_fields = ['id']
