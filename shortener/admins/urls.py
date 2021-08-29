from shortener.forms import UrlCreateForm
from shortener.admins.views import url_list
from django.contrib import admin
from django.urls import path

from rest_framework import routers
from shortener.urls.apis import *


urlpatterns = [
    path("", url_list, name="admin_url_list"),
]