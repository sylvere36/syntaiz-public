from rest_framework import serializers

from account.models import User
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field


from django.contrib.auth.password_validation import validate_password
import uuid


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # Générer un username unique
        unique_username = f"user_{uuid.uuid4().hex[:10]}"
        validated_data['username'] = unique_username
        user = super().create(validated_data)
        user.is_active = True
        user.is_staff = True
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'name', "classe", "age", "createdAt", "updatedAt"]


class AuthResponseSerializer(serializers.Serializer):
    """
    Serializer for the authentication response.
    """
    user = UserSerializer()
    token = serializers.CharField(help_text=_("Authentication token for the user."))

    @extend_schema_field(UserSerializer)
    def get_user(self, obj):
        return obj['user']
    
    @extend_schema_field(serializers.CharField())
    def get_token(self, obj):
        return obj['token']

