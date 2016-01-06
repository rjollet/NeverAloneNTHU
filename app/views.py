from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from .forms import UserProfileEditForm
from .models import UserProfile

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
    userProfile = get_object_or_404(UserProfile, user=request.user)
    pef = UserProfileEditForm(request.POST or None,instance=userProfile, prefix='profileedit')
    if pef.is_valid():
        pef.save()


    return render_to_response(template_name, dict(profileeditform=pef), context_instance=RequestContext(request))
