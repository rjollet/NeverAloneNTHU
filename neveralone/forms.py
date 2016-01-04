from django import forms
from django.forms import ModelForm
from app.models import UserProfile


class UserProfileCreationForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = ['gender', 'interested_in', 'dob']
        localized_fields = ('dob',)
