from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UserProfileEditForm, UsernameChangeForm
from .models import UserProfile

from django.contrib.auth.models import User
from app.models import Person, Picture


@login_required
def index(request):
    """
    If users are authenticated, direct them to the main page. Otherwise, take
    them to the login page.
    """
    user = request.user.pk
    userProfile = UserProfile.objects.get(user=request.user)
    person = Person.index.get(user_profile_id=userProfile.pk)
    interested_in_me = person.interested_in_me()
    matches = person.matches()
    potential_matches = person.potential_matches()

    return render_to_response('app/index.html', dict(interested_in_me=interested_in_me,matches=matches,potential_matches=potential_matches), context_instance=RequestContext(request))



@login_required
def profile(request, template_name='app/profile.html'):
    from django.contrib.auth import update_session_auth_hash
    user = User.objects.get(pk=request.user.pk)
    userProfile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        pef = UserProfileEditForm(request.POST or None, instance=userProfile, prefix='profileedit')
        ucf = UsernameChangeForm(request.POST or None, instance=user, prefix='usernamechange')
        if ucf.is_valid():
            user = ucf.save()
            user.save()
        if pef.is_valid():
            userProfile = pef.save()
            userProfile.save()
    pef = UserProfileEditForm(instance=userProfile, prefix='profileedit')
    ucf = UsernameChangeForm(instance=user, prefix='usernamechange')
    return render_to_response(template_name, dict(profileeditform=pef, usernamechangeform=ucf), context_instance=RequestContext(request))


@login_required
def pictures_page(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=request.user)
    person = Person.nodes.get(user_profile_id=userProfile.pk)

    if request.method == 'POST':
        data = dict(request.POST)

        looking_for_pictures = data.get('pictures', [])
        for picture in looking_for_pictures:
            person.looking_for.connect(Picture.nodes.get(pictureURL=picture))

    pictures = person.get_random_not_looking_for_pictures(limit=18)
    couple = person.get_random_couple()
    return render_to_response(
        'app/select_pictures.html',
        dict(pictures=pictures, couple=couple),
        context_instance=RequestContext(request))

@login_required
def interested_in_me(request, other=None):
    if request.method == 'POST' and other is not None:
        user = request.user
        userProfile = UserProfile.objects.get(user=request.user)
        person = Person.nodes.get(user_profile_id=userProfile.pk)
        other = Person.nodes.get(user_profile_id=other)
        person.interested_in_rel.connect(other)
    return HttpResponseRedirect('/app/')

@login_required
def recommended(request, p1=None, p2=None, answer=1):
    if request.method == 'POST' and p1 is not None and p2 is not None:
        add = 1 if answer is 1 else -1
        update = False
        person1 = Person.nodes.get(user_profile_id=p1)
        person2 = Person.nodes.get(user_profile_id=p2)
        if person1.recommanded.is_connected(person2):
            rel = person1.recommanded.relationship(person2)
            rel.weight += add
            rel.save()
        else:
            rel = person1.recommanded.connect(person2)
            rel.weight += add
            rel.save()

    return HttpResponseRedirect('/app/pictures')
