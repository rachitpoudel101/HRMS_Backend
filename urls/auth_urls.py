from django.urls import path
from apps.users.views import UserViewSet

urlpatterns = [
    path('', UserViewSet.as_view({'get': 'me'}), name='current-user'),
]
