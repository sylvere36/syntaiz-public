from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, exceptions
from rest_framework.permissions import AllowAny, IsAdminUser

from rest_framework.response import Response
from account.core.pagination import StandardResultsSetPagination
from account.serializers import UserSerializer, AuthResponseSerializer
from drf_spectacular.utils import extend_schema

from account.models import User
from rest_framework.parsers import JSONParser, MultiPartParser
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

class UserViewSet(viewsets.ModelViewSet):
    """ Gestion des utilisateurs. """
    queryset = User.objects.filter(deleted=False).order_by('-createdAt')
    parser_classes = (JSONParser, )
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['default_role', 'is_active']
    http_method_names = ['post',]

    permission_classes_by_action = {
        'login': [AllowAny],
        'create': [AllowAny],
        'list': [IsAdminUser]}
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    @extend_schema(
        request=UserSerializer,
        responses=AuthResponseSerializer,
        operation_id=_("Login User"),
        description=_("Login user and return user data with token."),
    )
    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True
            user.save()

            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        else:
            raise exceptions.ValidationError(serializer.errors)

