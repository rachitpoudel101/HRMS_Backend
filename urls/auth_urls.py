from django.urls import path
from apps.users.views import UserViewSet, get_current_user

urlpatterns = [
    path('', get_current_user, name='current-user'),
]
