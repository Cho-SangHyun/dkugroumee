from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=15)
    email = models.CharField(max_length=50, default='')
    profile = models.ImageField(blank=True, null=True, upload_to="images/")