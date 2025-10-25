from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


# Gestionnaire d'utilisateur
class UserManager(BaseUserManager):
    use_in_migrations = True

    # methode permettant de créer un utilisateur en général
    def _create_user(self, email, username, password, save=True, **extra_field):
        if not email:
            raise ValueError("Entrer une adresse email valide")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(email=email, username=username, **extra_field)
        user.set_password(password)
        if save:
            user.save(using=self._db)
        return user

    def create_user(self, email, username, password, save=True, **extra_field):
        extra_field.setdefault('is_superuser', False)
        extra_field.setdefault('default_role', "user")
        extra_field.setdefault('date_joined', timezone.localtime(timezone.now()).date().today)
        extra_field.setdefault('last_login', timezone.now())
        return self._create_user(email, username, password, save, **extra_field)

    def create_superuser(self, email, username, password, save=True, **extra_field):
        extra_field.setdefault('is_superuser', True)
        extra_field.setdefault('is_staff', True)
        extra_field.setdefault('default_role', "super-admin")
        return self._create_user(email, username, password, save, **extra_field)