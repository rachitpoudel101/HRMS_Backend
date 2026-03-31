from apps.notice.models import Notic, NoticeType, NoticeAttachment
from apps.notice.serializers.serializers import (
    NoticSerializer,
    NoticListSerializer,
    NoticCreateUpdateSerializer,
    NoticeTypeSerializer,
    NoticeTypeListSerializer,
    NoticeAttachmentSerializer,
    NoticeAttachmentListSerializer,
)
from apps.common.mixins.abstract_viewset import AbstractViewSet
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from apps.common.permissions.permissions import IsAdminOrHROrSuperAdmin


class NoticViewSet(AbstractViewSet, CompanyFilterMixin):
    """
    ViewSet for managing Notice records
    Only Admin, HR, and SuperAdmin can create/update/delete notices
    """

    queryset = (
        Notic.objects.select_related("branch", "created_by", "updated_by")
        .prefetch_related("employees", "attachments")
        .all()
    )
    serializer_class = NoticSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHROrSuperAdmin]
    filterset_fields = ["branch", "date", "name"]
    search_fields = ["name", "description"]
    ordering_fields = ["date", "name", "created_at"]
    ordering = ["-date"]

    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == "list":
            return NoticListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return NoticCreateUpdateSerializer
        return NoticSerializer


class NoticeTypeViewSet(AbstractViewSet, CompanyFilterMixin):
    """
    ViewSet for managing Notice Type records
    Only Admin, HR, and SuperAdmin can create/update/delete notice types
    """

    queryset = NoticeType.objects.select_related("created_by", "updated_by").all()
    serializer_class = NoticeTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHROrSuperAdmin]
    filterset_fields = ["type_name"]
    search_fields = ["type_name", "description"]
    ordering_fields = ["type_name", "created_at"]
    ordering = ["type_name"]

    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == "list":
            return NoticeTypeListSerializer
        return NoticeTypeSerializer


class NoticeAttachmentViewSet(AbstractViewSet, CompanyFilterMixin):
    """
    ViewSet for managing Notice Attachment records
    Only Admin, HR, and SuperAdmin can create/update/delete notice attachments
    """

    queryset = NoticeAttachment.objects.select_related(
        "notice", "created_by", "updated_by"
    ).all()
    serializer_class = NoticeAttachmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHROrSuperAdmin]
    filterset_fields = ["notice"]
    search_fields = ["description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == "list":
            return NoticeAttachmentListSerializer
        return NoticeAttachmentSerializer
