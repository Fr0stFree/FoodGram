from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserRole


@receiver(post_save, sender=User)
def create_favorites(sender, instance, created, **kwargs):
    if created:
        UserRole.objects.create(user=instance)
