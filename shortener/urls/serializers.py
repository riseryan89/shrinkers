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
        fields = ["id", "nick_name", "prefix", "shortened_url", "creator", "click", "create_via", "expired_at"]
