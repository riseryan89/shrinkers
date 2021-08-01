import string
import random

from django.db import models
from django.contrib.auth.models import User as U
from django.contrib.auth.models import AbstractUser

# Create your models here.


class PayPlan(models.Model):
    name = models.CharField(max_length=20)
    price = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)


class Users(AbstractUser):
    full_name = models.CharField(max_length=100, null=True)
    pay_plan = models.ForeignKey(PayPlan, on_delete=models.DO_NOTHING, null=True)


class ShortenedUrls(models.Model):
    class UrlCreatedVia(models.TextChoices):
        WEBSITE = "web"
        TELEGRAM = "telegram"

    def rand_string():
        str_pool = string.digits + string.ascii_letters
        return ("".join([random.choice(str_pool) for _ in range(6)])).lower()

    nick_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE)
    target_url = models.CharField(max_length=2000)
    shortened_url = models.CharField(max_length=6, default=rand_string)
    created_via = models.CharField(max_length=8, choices=UrlCreatedVia.choices, default=UrlCreatedVia.WEBSITE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
