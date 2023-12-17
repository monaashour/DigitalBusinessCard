from django.db import models


class Card(models.Model):
    qr_b64 = models.TextField()
    photo_b64 = models.TextField(null=True, default=None)
    linkedin_url = models.URLField(null=True, default=None)
    phone = models.CharField(max_length=20, null=True, default=None)
    job_title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)