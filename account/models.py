from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as text

from account.managers import UserManager
from django.utils import timezone


def profil_directory_path(instance, filename):
    filename = filename.lower()
    return 'profil_image_{0}/{1}'.format(instance.profil_image, filename)

Roles = (
    ('user', text('Utilisateur')),
    ('admin', text('Administrateur')),
    ('super_admin', text('Super Administrateur')),
)


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=text("Nom"),  null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name=text("Nom d'utilisateur"), unique=True, null=True, blank=True)
    classe = models.CharField(max_length=255, verbose_name=text("classe"),  null=True, blank=True)
    sexe = models.CharField(max_length=10, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=text("Actif"))
    default_role = models.CharField(choices=Roles, max_length=30, default='user')
    is_superuser = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["age", "name"]

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Utilisateur'
