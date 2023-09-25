from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.s3 import S3Boto3StoragePublic


class UserManager(BaseUserManager):
    """ User Model Manager """

    def create_user(self, username, password=None,
                    is_staff=False, is_superuser=False, is_active=True):
        if not username:
            raise ValueError('Users must have email Address')
        if not password:
            raise ValueError('User must have Password')
        # if not full_name:
        #     raise ValueError('User must have a full name')

        user_obj = self.model(
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        user_obj.set_password(password)
        user_obj.save(using=self._db)

    def create_staffuser(self, username, password=None):
        user = self.create_user(
            username,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom abstract user Model.
    """
    # Names
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    # contact
    username = models.EmailField(_('email address'), unique=True)  # require
    number = models.PositiveIntegerField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar',
                               default=None,
                               null=True,
                               storage=S3Boto3StoragePublic(),
                               blank=True)
    is_light = models.BooleanField(default=False)
    # Registration
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Permission
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # Main Field for authentication
    USERNAME_FIELD = 'username'
    marketplace = models.ForeignKey("marketplace.Marketplace", null=True, blank=True,  on_delete=models.SET_NULL)
    # permissions
    objects = UserManager()

    # When user create must need to fill this field
    REQUIRED_FIELDS = []

    @property
    def email(self):
        return self.username

    @property
    def photo_url(self):
        if self.avatar:
            return self.avatar.url
        from django.templatetags.static import static

        return static("images/avatar_default.png")

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('-created_at', '-updated_at',)

    def get_full_name(self):
        if self.first_name:
            return f'{self.first_name}  {self.last_name}'
        return self.username.split('@')[0]

    def get_email_field_name(*args):
        return "username"
