import json
from shortener.forms import LoginForm
from django.contrib.auth.models import User
from shortener.models import ShortenedUrls, TrackingParams, Users
from django.test import TestCase
from django.test import Client
from unittest.mock import patch


# Create your tests here.
class ModelTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(password="12341234", username="abcdefg", email="test@test.com")
        users = Users.objects.create(full_name="abcdefg", user_id=user.id)
        ShortenedUrls.objects.create(nick_name="new_url", target_url="abc.com.co.kr", creator_id=users.id)

    def test_click(self):
        """clicked() 메소드 테스트"""
        new_url = ShortenedUrls.objects.get(nick_name="new_url")
        self.assertEqual(new_url.click, 0)
        new_url.clicked()
        self.assertEqual(new_url.click, 1)

    def test_get_flat_params(self):
        """flat params 테스트"""
        shortened_url = ShortenedUrls.objects.all().first()
        TrackingParams.objects.create(shortened_url=shortened_url, params="hello")
        TrackingParams.objects.create(shortened_url=shortened_url, params="world")
        flat_params = TrackingParams.get_tracking_params(shortened_url.id)
        self.assertEqual(list(flat_params), ["hello", "world"])


class AuthTest(TestCase):
    def setUp(self):
        User.objects.create(password="12341234", username="abcdefg", email="test@test.com")

    def test_register(self):
        """register 테스트"""
        c = Client()
        body = {"email": "test@test.com", "name": "Test User", "password": "1234123", "policy": True}
        res = c.post("/ninja-api/users/register", json.dumps(body), content_type="application/json")
        # password length < 7
        self.assertEqual(res.status_code, 422)

        body = {"email": "testest.com", "name": "Test User", "password": "12341235", "policy": True}
        res = c.post("/ninja-api/users/register", json.dumps(body), content_type="application/json")
        # email validation
        self.assertEqual(res.status_code, 422)

        body = {"email": "test@test.com", "name": "Test User", "password": "12341235", "policy": False}
        res = c.post("/ninja-api/users/register", json.dumps(body), content_type="application/json")
        # policy validation
        self.assertEqual(res.status_code, 422)

        body = {"email": "test@test.com", "name": "Test User", "password": "12341235", "policy": True}
        res = c.post("/ninja-api/users/register", json.dumps(body), content_type="application/json")
        # Email Duplicate
        self.assertEqual(res.status_code, 409)

        body = {"email": "test1@test.com", "name": "Test User", "password": "12341235", "policy": True}
        res = c.post("/ninja-api/users/register", json.dumps(body), content_type="application/json")
        # Email Duplicate
        self.assertEqual(res.status_code, 201)

    @patch("shortener.middleware.ShrinkersMiddleware.log_action", return_value="Mock!")
    def test_login(self, mock):
        """login 테스트"""
        c = Client()
        body = {"email": "test11@test.com", "password": "12341235", "remember_me": True}
        res = c.post("/login", body)
        # No Matched User
        self.assertEqual(res.status_code, 200)


class UrlManagementTest(TestCase):
    def setUp(self):
        user = User.objects.create(password="12341234", username="abcdefg", email="test@test.com")
        Users.objects.create(full_name="abcdefg", user_id=user.id)

    def test_delete(self):
        users = Users.objects.filter(user__email="test@test.com").first()
        url = ShortenedUrls.objects.create(nick_name="new_url", target_url="abc.com.co.kr", creator_id=users.id)
        c = Client()
        c.force_login(users.user)
        """ URL 삭제 테스트 """
        res = c.delete(f"/api/urls/{url.id}/")
        self.assertEqual(res.status_code, 200)
        """ 매치 하는 URL 없음 """
        res = c.delete(f"/api/urls/0/")
        self.assertEqual(res.status_code, 404)
