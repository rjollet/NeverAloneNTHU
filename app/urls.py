from django.contrib.auth.forms import AdminPasswordChangeForm
from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/passwordchange/$',
        'django.contrib.auth.views.password_change',
        {'post_change_redirect': '/app/profile/'},
        name="password_change"),
    url(r'^pictures/$', views.pictures_page, name='pictures_page'),
]
