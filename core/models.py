# -*- coding: utf-8 -*-

import os

from django.db import models
from django.contrib.auth.models import AbstractUser


def _get_file_path(user, filename):
    return os.path.join('user_{0}'.format(user.username), filename)


class User(AbstractUser):
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to=_get_file_path)

