from shortener.models import Users
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['username', 'email', 'password']