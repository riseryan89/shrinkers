from shortener.forms import UrlCreateForm
from shortener.urls.views import url_change, url_list, url_create
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("", url_list, name="url_list"),
    path("create", url_create, name="url_create"),
    path("<str:action>/<int:url_id>", url_change, name="url_change"),
]
