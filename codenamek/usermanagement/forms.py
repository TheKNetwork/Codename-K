from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms

from codenamek.usermanagement.models import UserProfile
 
 
class ProfileForm(ModelForm):
  class Meta:
      model = UserProfile
      exclude = ('user',)


class RegistrationForm(forms.Form):
    username = forms.CharField(label=('Username'), required=True)
    email = forms.EmailField(label=('Email'), required=True)

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        email = cleaned_data.get('email', None)
        username = cleaned_data.get('username', None)

        users = User.objects.filter(email=email)
        if len(users) > 0:
            raise forms.ValidationError('User with such email already exists')

        users = User.objects.filter(username=username)
        if len(users) > 0:
            raise forms.ValidationError('This username is already taken.')
        return cleaned_data


class PasswordForm(forms.Form):
    password = forms.CharField( widget=forms.PasswordInput, label="Password", required=True)
    password_confirm = forms.CharField( widget=forms.PasswordInput, label="Confirmation", required=True)

    def clean(self):
        cleaned_data = super(PasswordForm, self).clean()
        password = cleaned_data.get('password', None)
        password_confirm = cleaned_data.get('password_confirm', None)
        if password != password_confirm:
            raise forms.ValidationError('Passwords are not the same')
        return cleaned_data
