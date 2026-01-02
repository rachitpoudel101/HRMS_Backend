from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, CompanyViewSet, BranchViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'employees', EmployeeViewSet, basename='employee')


urlpatterns = [
	path('', include(router.urls)),
]

