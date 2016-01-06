from django import forms
from django.forms import ModelForm
from app.models import UserProfile


class UserProfileEditForm(ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('user',)
        localized_fields = ('dob',)
