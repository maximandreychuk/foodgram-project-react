from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Emai', max_length=100, unique=True)
    username = models.CharField(
        'Имя пользователя',
        max_length=100,
        unique=True)
    password = models.CharField('Пароль', max_length=100)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_following',
        )

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
