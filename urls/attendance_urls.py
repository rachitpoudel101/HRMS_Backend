from rest_framework.routers import DefaultRouter
from apps.attendance.views import AttendanceViewSet, FingerprintScanViewSet

router = DefaultRouter()
router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(
    r"fingerprint-scans", FingerprintScanViewSet, basename="fingerprintscan"
)

urlpatterns = router.urls
