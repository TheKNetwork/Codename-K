from django.conf.urls.defaults import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout
from codenamek.usermanagement.forms import ProfileForm

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^homeroom/$', 'codenamek.usermanagement.views.index', name='homeroom'),
    url(r'^class/session/$', 'codenamek.whiteboard.views.index'),
    url(r'^accounts/', include('registration.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # added for registration backend
    url(r'^accounts/register/$', 'usermanagement.views.register',
        {'backend': 'usermanagement.registration_backend.RegistrationBackend'},
        name='registration_register'
    ),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        'usermanagement.views.activate',
        {'backend': 'usermanagement.registration_backend.RegistrationBackend'},
        name='registration_activate'
    ),

    # CAUTION - These next two lines MUST be in the correct order
    ('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm, }), # 1
    (r'^profiles/', include('profiles.urls')), # 2
    
    # khan-academy api urls
    url(r'^khan-academy/auth/$', 'usermanagement.views.request_token', name='request-token'),
    url(r'^khan-academy/auth/callback/$', 'usermanagement.views.access_token', name='access-token'),
    url(r'^khan-academy/api/test/$', 'usermanagement.views.khan_api_test', name='api-test'),
    
    # django socket io
    url("", include("django_socketio.urls")),
    url("^chat", include("codenamek.chat.urls")),
)

urlpatterns += staticfiles_urlpatterns()
