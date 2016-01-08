from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template import RequestContext

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .forms import UserProfileCreationForm

from app.models import Person


def main_page(request):
    if request.user.is_authenticated():
        user = request.user.id
        person = Person.index.get(user_profile_id=user)
        interested_in_me = person.interested_in_me()
        matches = person.matches()
        potential_matches = person.potential_matches()

        return render_to_response('app/index.html', dict(interested_in_me=interested_in_me,matches=matches,potential_matches=potential_matches), context_instance=RequestContext(request))
        #return HttpResponseRedirect('/app/')
    af = AuthenticationForm()
    uf = UserCreationForm(prefix='user')
    upf = UserProfileCreationForm(prefix='userprofile')
    return render_to_response('index.html', dict(authform=af, userform=uf, userprofileform=upf), context_instance=RequestContext(request))


def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    logout(request)
    return HttpResponseRedirect('/')


def register(request):
    if request.method == 'POST':
        uf = UserCreationForm(request.POST, prefix='user')
        upf = UserProfileCreationForm(request.POST, prefix='userprofile')
        if uf.is_valid() * upf.is_valid():

            newUser = uf.save()
            userprofile = upf.save(commit=False)
            userprofile.user = newUser
            userprofile.save()

            user = authenticate(username=uf.cleaned_data['username'], password=uf.cleaned_data['password1'])
            if user is not None:
                # the password verified for the auth
                if user.is_active:
                    login(request, user)
                    print("User is valid, active and authenticated")
                    return HttpResponseRedirect('/app/')

    af = AuthenticationForm()
    return render_to_response('index.html', dict(authform=af, userform=uf, userprofileform=upf), context_instance=RequestContext(request))
