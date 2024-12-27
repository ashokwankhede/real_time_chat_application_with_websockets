from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AppUsers


class AppUserRegistrationForm(UserCreationForm):
    mobile_no = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = AppUsers
        fields = ['username', 'email', 'password1', 'password2', 'mobile_no', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
    




class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)