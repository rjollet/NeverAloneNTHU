from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UserProfileEditForm
from .models import UserProfile

from app.models import Person, Picture


@login_required
def index(request):
    """
    If users are authenticated, direct them to the main page. Otherwise, take
    them to the login page.
    """
    return render_to_response('app/index.html')


@login_required
def profile(request, template_name='app/profile.html'):
    user = request.user
    userProfile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        pef = UserProfileEditForm(request.POST, instance=userProfile, prefix='profileedit')
        if pef.is_valid():
            print("VALIDE")
            userProfile = pef.save()
    pef = UserProfileEditForm(instance=userProfile, prefix='profileedit')
    return render_to_response(template_name, dict(profileeditform=pef), context_instance=RequestContext(request))


@login_required
def pictures_page(request):
    user = request.user
    person = Person.nodes.get(user_profile_id=user.pk)

    if request.method == 'POST':
        data = dict(request.POST)

        looking_for_pictures = data.get('pictures', [])
        for picture in looking_for_pictures:
            person.looking_for.connect(Picture.nodes.get(pictureURL=picture))

    pictures = person.get_random_not_looking_for_pictures(limit=18)

    return render_to_response(
        'app/select_pictures.html',
        dict(pictures=pictures),
        context_instance=RequestContext(request))
