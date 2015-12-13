from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from .forms import SigninForm




def main_page(request):
    return render_to_response('index.html')

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    logout(request)
    return HttpResponseRedirect('/')

def signin(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SigninForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            userform = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
            userform.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # the password verified for the auth
                if user.is_active:
                    login(request, user)
                    print("User is valid, active and authenticated")
                    return HttpResponseRedirect('/app/')
                else:
                    print("The password is valid, but the account has been disabled!")
                    return HttpResponseRedirect('/signin/')
            else:
                # the authentication system was unable to verify the username and password
                print("The username and password were incorrect.")
                return HttpResponseRedirect('/signin/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SigninForm()

    return render(request, 'signin.html', {'form': form})
