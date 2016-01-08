from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UserProfileEditForm, UsernameChangeForm
from .models import UserProfile

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def index(request):
    """
    If users are authenticated, direct them to the main page. Otherwise, take
    them to the login page.
    """
    user = request.user.pk
    userProfile = UserProfile.objects.get(user=request.user)
    return render_to_response('app/index.html',dict(profile=userProfile), context_instance=RequestContext(request))

@login_required
def profile(request, template_name='app/profile.html'):
    user = User.objects.get(pk=request.user.pk)
    userProfile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':

        pef = UserProfileEditForm(request.POST, instance=userProfile, prefix='profileedit')
        ucf = UsernameChangeForm(request.POST, instance=user, prefix='userchange')
        if request.POST.get('usernamechange-email') is not None: user.email = request.POST.get('usernamechange-email')
        if request.POST.get('usernamechange-username') is not None: user.username = request.POST.get('usernamechange-username')
        user.save()
        if pef.is_valid():
            userProfile = pef.save()
            userProfile.save()
    pef = UserProfileEditForm(instance=userProfile, prefix='profileedit')
    ucf = UsernameChangeForm(instance=user, prefix='usernamechange')
    return render_to_response(template_name, dict(profileeditform=pef, usernamechangeform=ucf), context_instance=RequestContext(request))
