import re
import requests
from shortener.utils import url_count_changer
from django.contrib.auth.models import User
from shortener.models import Users, ShortenedUrls
from rest_framework import serializers


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


class UserSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)

    class Meta:
        model = Users
        fields = ["id", "url_count", "organization", "user"]


class UrlListSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = ShortenedUrls
        fields = "__all__"


class BrowerStatSerializer(serializers.Serializer):
    web_browser = serializers.CharField(max_length=50)
    count = serializers.IntegerField()
    date = serializers.DateField(source="created_at__date", required=False)


class UrlCreateSerializer(serializers.Serializer):
    nick_name = serializers.CharField(max_length=50)
    target_url = serializers.CharField(max_length=2000)
    category = serializers.IntegerField(required=False)

    def create(self, request, data, commit=True):
        instance = ShortenedUrls()
        users = Users.objects.filter(request.users_id).first()
        instance.creator = users
        instance.category = data.get("category", None)
        instance.target_url = data.get("target_url").strip()
        if commit:
            try:
                instance.save()
            except Exception as e:
                print(e)
            else:
                url_count_changer(request, True)
        return instance
