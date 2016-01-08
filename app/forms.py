from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from app.models import UserProfile


class UserProfileEditForm(ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('user',)
        localized_fields = ('dob',)

class UsernameChangeForm(ModelForm):

    class Meta:
        model = User
        fields = ['username','email',]
