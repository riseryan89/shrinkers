from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from shortener.models import Users


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
