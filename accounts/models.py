from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Phone Number'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Approved by Admin'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')