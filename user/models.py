import string
import uuid

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_mysql.models import Model


class MyBaseModel(Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """
    Custom model manager

    Arguments:
        BaseUserManager -- To define a custom manager that extends BaseUserManager
                                providing two additional methods

    Raises:
        TypeError -- It raises if the password is not provided while creating the users.

    Returns:
        user_object -- This will override the default model manager and returns user object.
    """

    def create_user(self, email=None, password=None):
        if not email:
            raise TypeError('Users must have valid email address.')

        user = self.model(email=email, password=password)
        user.set_password(password)
        # user.is_active = True     Default value is True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        if not email:
            raise TypeError('Users must have valid email address.')
        if password is None:
            raise TypeError('Superusers must have a password.')
        user = self.create_user(email=email, password=password)
        # user.is_active = True     Default value is already True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class AppUser(AbstractBaseUser, PermissionsMixin, MyBaseModel):
    """
    Class to create Custom Auth User Model

    Arguments:
        AbstractBaseUser -- Here we are subclassing the Django AbstractBaseUser,
                                which comes with only three fields:
                                1 - password
                                2 - last_login
                                3 - is_active
                            It provides the core implementation of a user model,
                                including hashed passwords and tokenized password resets.

        PermissionsMixin -- The PermissionsMixin is a model that helps you implement
                                permission settings as-is or
                                modified to your requirements.
    """

    email = models.EmailField(max_length = 254, unique=True, db_index=True)

    full_name = models.CharField(max_length=400, null=True)

    is_active = models.BooleanField(default=False, db_index=True)

    email_verified = models.BooleanField(default=True, db_index=True)

    auth_token = models.CharField(max_length=400, null=True)

    is_deleted = models.BooleanField(default=False, db_index=True)

    is_admin = models.BooleanField(default=False)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(AppUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.email
