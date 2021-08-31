from shortener.forms import LoginForm
from django.contrib.auth.models import User
from shortener.models import ShortenedUrls, TrackingParams, Users
from django.test import TestCase

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


