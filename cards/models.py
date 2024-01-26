from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, primary_key=True)
    photo_b64 = models.TextField(null=True, default=None)
    linkedin = models.URLField(null=True, default=None)
    phone = models.CharField(max_length=30, null=True, default=None)
    job_title = models.CharField(max_length=300)
    region = models.CharField(max_length=20, default='Europe')
    is_active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)