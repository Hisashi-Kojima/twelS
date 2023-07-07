from django.core.exceptions import ValidationError
from django.core.mail import send_mail as send
from django.contrib.auth import login, logout
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def email_validater(email):
    if "saga-u.ac.jp" not in email:
        raise ValidationError("saga-u.ac.jpを含むアドレスを使ってください")


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        _('email address'), unique=True, validators=[email_validater])

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    # TODO: 退会時にFalseになるようにする。
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            '"is_active" indicates whether this user is active.'
            'Unselect this instead of deleting accounts.'
            'True if the user has completed registration, False if the user is in a temporary registration state.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def send_mail(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        from_email = '22801001@edu.cc.saga-u.ac.jp'
        send(subject, message, from_email, [self.email], **kwargs)


class IPAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_access = models.DateTimeField(_('last access'), default=timezone.now)

    def __str__(self):
        return f"{self.user.email} ({self.ip_address})"


class PasswordResetRequest(models.Model):
    email = models.EmailField(_('email address'), unique=True)
    email_request_times = models.PositiveSmallIntegerField(
        _('email request times'),
        default=0,
        help_text=_(
            'Designates how many times this user sent email-request for certification'
        ),
    )
    first_request_date = models.DateTimeField(_('first request date'), blank=True, null=True)

    def __str__(self):
        return self.email


class UserCreateRequest(models.Model):
    email = models.EmailField(_('email address'), unique=True)
    email_request_times = models.PositiveSmallIntegerField(
        _('email request times'),
        default=0,
        help_text=_(
            'Designates how many times this user sent email-request for certification'
        ),
    )
    first_request_date = models.DateTimeField(_('first request date'), blank=True, null=True)

    def __str__(self):
        return self.email


class EmailUser(AbstractBaseUser):
    """メール認証ログイン用の一時的なユーザ"""
    email = models.EmailField(
        _('email address'), unique=True, validators=[email_validater])
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Unselect this instead of deleting accounts.'
            '"is_active" indicates whether this Emailuser is currently logged in.'
        ),
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def send_mail(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        from_email = '22801001@edu.cc.saga-u.ac.jp'
        send(subject, message, from_email, [self.email], **kwargs)
    
    def login(self, request):
        self.is_active = True
        self.save()
        login(request, self, backend='login.auth_backend.PasswordlessAuthBackend')
    
    def logout(self, request):
        self.is_active = False
        self.save()
        logout(request)


class EmailLoginRequest(models.Model):
    email = models.EmailField(_('email address'), unique=True)
    email_request_times = models.PositiveSmallIntegerField(
        _('email request times'),
        default=0,
        help_text=_(
            'Designates how many times this user sent email-request for certification'
        ),
    )
    first_request_date = models.DateTimeField(_('first request date'), blank=True, null=True)

    def __str__(self):
        return self.email
