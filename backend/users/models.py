from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    # ИЗМЕНЕНИЕ 1: Возвращаем username как поле для логина
    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email Address'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.')],
        verbose_name='Username'
    )
    first_name = models.CharField(max_length=150, verbose_name='First Name')
    last_name = models.CharField(max_length=150, verbose_name='Last Name')
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user} follows {self.author}'
