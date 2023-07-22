from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserRole(models.Model):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLES = (
        (USER, "user"),
        (MODERATOR, "moderator"),
        (ADMIN, "admin"),
    )

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=USER,
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

    @property
    def is_moderator(self):
        return any(
            (
                self.user.is_superuser,
                self.user.is_staff,
                self.role == self.MODERATOR,
                self.role == self.ADMIN,
            )
        )

    @property
    def is_admin(self):
        return any((self.user.is_superuser, self.role == self.ADMIN))


class Follow(models.Model):
    follower = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("follower", "author"),
                name="uniq_follow",
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("author")),
                name="self_follow_restriction",
            ),
        ]
