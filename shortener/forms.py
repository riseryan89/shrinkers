from urllib.parse import urlparse

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import Widget
from shortener.models import ShortenedUrls, Users
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=30, required=False, help_text="Optional.", label="이름")
    username = forms.CharField(max_length=30, required=False, help_text="Optional.", label="유저명")
    email = forms.EmailField(max_length=254, help_text="Required. Inform a valid email address.", label="이메일")

    class Meta:
        model = Users
        fields = (
            "username",
            "full_name",
            "email",
            "password1",
            "password2",
        )


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "이메일"})
    )
    password = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "패스워드"}),
    )
    remember_me = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "custom-control-input", "id": "_loginRememberMe"}),
        required=False,
        disabled=False,
    )


class UrlCreateForm(forms.ModelForm):
    class Meta:
        model = ShortenedUrls
        fields = ["nick_name", "target_url"]
        labels = {
            "nick_name": _("별칭"),
            "target_url": _("URL"),
        }
        widgets = {
            "nick_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "URL을 구분하기 위한 별칭"}),
            "target_url": forms.TextInput(attrs={"class": "form-control", "placeholder": "포워딩될 URL"}),
        }

    def save(self, request, commit=True):
        instance = super(UrlCreateForm, self).save(commit=False)
        instance.created_by_id = request.user.id
        instance.target_url = instance.target_url.strip()
        if commit:
            instance.save()
        return instance

    def update_form(self, request, url_id):
        instance = super(UrlCreateForm, self).save(commit=False)
        instance.target_url = instance.target_url.strip()
        ShortenedUrls.objects.filter(pk=url_id, created_by_id=request.user.id).update(
            target_url=instance.target_url, nick_name=instance.nick_name
        )
