from django import forms

class SigninForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()