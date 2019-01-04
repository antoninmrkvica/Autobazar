from django.db import models

# Create your models here.

class User(models.Model):
    is_admin = models.BooleanField(default=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
