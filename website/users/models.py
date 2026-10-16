from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    description = models.TextField(null=True, blank=True, verbose_name="Описание профиля")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="Аватар")
