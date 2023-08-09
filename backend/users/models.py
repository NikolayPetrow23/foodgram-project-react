from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class RoleUser(models.TextChoices):
        user = "user", _("Аутентифицированный пользователь")
        admin = "admin", _("Администратор")

    email = models.EmailField(
        _('email address'),
        unique=True,
        max_length=254
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    role = models.CharField(
        max_length=20, default=RoleUser.user, choices=RoleUser.choices
    )
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ("id",)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = "Подписку"
        verbose_name_plural = "Подписки"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="author_not_user"
            ),
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_author_unique"),
        ]
