from django import forms
from django.forms import ModelForm
from app.models import UserProfile


class UserProfileSigninForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = ['gender', 'sexuality', 'dob']
        localized_fields = ('dob',)

