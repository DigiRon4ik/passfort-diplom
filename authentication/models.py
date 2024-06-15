from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

from posixpath import join as posixpath_join
from os import remove as os_remove

from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy


def user_avatar_upload_to(instance, filename):
    ext = filename.split(".")[-1]  # Получаем расширение файла
    # Если файл уже существует, удаляем его
    if img := get_user_model().objects.get(username=instance.username).img:
        os_remove(img.path)
    # Генерируем новое имя файла "{username}-avatar.{ext}"
    filename = f"{instance.username}-avatar.{ext}"
    # Собираем путь к новому файла "avatars/{username}-avatar.{ext}"
    return posixpath_join("avatars", filename)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    master_password = models.CharField(
        max_length=256, verbose_name="Мастер-Пароль", null=True
    )
    img = models.ImageField(
        upload_to=user_avatar_upload_to,
        verbose_name="Аватар",
        blank=True,
        null=True,
    )

    def get_master_password_from_session(self, request):
        return request.session.get("master_password")

    def save(self, *args, **kwargs):
        if self.pk is None:  # Если это создание нового пользователя
            self.master_password = make_password(self.master_password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
