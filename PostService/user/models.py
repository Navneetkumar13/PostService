from django.db import models

class User(models.Model):
    name = models.CharField(max_length=256)
    username = models.CharField(max_length=1000, unique=True)
    country_code = models.CharField(max_length=10, null=True)
    phone_number = models.BigIntegerField(null=True)
    email = models.EmailField(unique=True)
    password = models.BinaryField(default = None, null=True)
    key = models.BinaryField(default= None, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True)
