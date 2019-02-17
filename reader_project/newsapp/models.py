from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class rss_field(models.Model):
    feed_link=models.CharField(max_length=200)
    created_by=models.CharField(max_length=100)

class news(models.Model):
    title=models.CharField(max_length=400)
    summary=models.CharField(max_length=400)
    link=models.CharField(max_length=400)
    feed_link=models.CharField(max_length=200)
    created_at=models.DateTimeField(auto_now_add=True)

class user_filter(models.Model):
    owned_by=models.CharField(max_length=100)
    keywds=models.CharField(max_length=1000)




