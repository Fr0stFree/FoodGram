from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserRole


@receiver(post_save, sender=User)
def setup_role(sender, instance, created, **kwargs):
    if created:
        UserRole.objects.create(user=instance)


@receiver(post_save, sender=UserRole)
def setup_role_permissions(sender, instance, created, **kwargs):
    if instance.role == UserRole.USER:
        instance.user.is_superuser = False
        instance.user.is_staff = False

    elif instance.role == UserRole.MODERATOR:
        instance.user.is_staff = True
        instance.user.is_superuser = False

    elif instance.role == UserRole.ADMIN:
        instance.user.is_superuser = True
        instance.user.is_staff = True

    instance.user.save()
