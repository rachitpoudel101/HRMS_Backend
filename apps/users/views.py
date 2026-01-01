from apps.common.mixins.abstract_viewset import AbstractViewSet
from apps.users.models import User
from apps.users.serializers.company_serializers import CompanySerializer
from apps.users.serializers.users_serializers import UserSerializer
from apps.users.models import Company

class UserViewSet(AbstractViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []
class CompanyViewSet(AbstractViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = []

    def get_queryset(self):
        """Optionally restricts the returned companies to a given user,
        by filtering against a `user_id` query parameter in the URL.
        """
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(users__id=user_id)
        return queryset
