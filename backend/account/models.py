from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from datetime import datetime
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.


# user model
class CustomUser(AbstractUser):
    tg_token = models.CharField(max_length=255, blank=True, null=True)
    chat_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    is_executor = models.BooleanField(default=False)
    avatar = models.ImageField(blank=True, null=True)

    def get_business_profile(self):
        try:
            return self.business_profile
        except:
            return None

    def full_name(self):
        first_name = self.first_name
        last_name = self.last_name

        full_name = ""

        if first_name:
            full_name += first_name

            if last_name:
                full_name += ' ' + last_name

        return full_name

    def save(self, *args, **kwargs):
        bp = self.get_business_profile()

        if bp:
            self.is_executor = True

        return super().save(*args, **kwargs)


# user's busines model
class BusinessProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    organization = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    business_avatar = models.ImageField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.user:
            self.user.is_executor = self.active
            self.user.save()

        return super().save(*args, **kwargs)


@receiver(pre_delete, sender=BusinessProfile)
def business_profile_delete(sender, instance, **kwargs):
    if instance.user:
        instance.user.is_executor = False
        instance.user.save()
