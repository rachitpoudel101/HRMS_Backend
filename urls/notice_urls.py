from rest_framework.routers import DefaultRouter
from apps.notice.views import NoticViewSet, NoticeTypeViewSet, NoticeAttachmentViewSet

router = DefaultRouter()
router.register(r"notices", NoticViewSet, basename="notice")
router.register(r"notice-types", NoticeTypeViewSet, basename="noticetype")
router.register(
    r"notice-attachments", NoticeAttachmentViewSet, basename="noticeattachment"
)

urlpatterns = router.urls
