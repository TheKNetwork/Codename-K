from django.conf.urls.defaults import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout
from codenamek.usermanagement.forms import *
from codenamek.schools.forms import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),
    
    # All urls in this section are from the perspective of the user,
    # and therefore should be of the pattern /username/something/something_else
    #     This one comes from the user management app
    # TODO: Put these in the usermanagement's urls.py
    url(r'^(?P<user_name>\w+)/homeroom/$', 'codenamek.usermanagement.views.index', name='homeroom'),
    url(r'^homeroom/$', 'codenamek.usermanagement.views.homeroom_failsafe', name='homeroom_safe'),
    
    #     These urls come from the schools app
    # TODO: Put these in the schools urls.py
    url(r'^(?P<user_name>\w+)/schools/(?P<_school_id>\d+)/create_a_class','codenamek.schools.views.create_a_class'),
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)','codenamek.schools.views.class_congregation', name='class_congregation'),
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)','codenamek.schools.views.classes_for_school', name='schools_class'),
    url(r'^(?P<user_name>\w+)/schools/$', 'codenamek.schools.views.index', name='schools'),
    
    url(r'^class/session/$', 'codenamek.whiteboard.views.index'),
    
    url("^chat/$", "chat.views.rooms", name="rooms"),
    url("^chat/create/$", "chat.views.create", name="create"),
    url("^chat/system_message/$", "chat.views.system_message", name="system_message"),
    # url("^chat/(?P<slug>.*)$", "chat.views.room", name="room"),
    url("^chat/(?P<school_id>\d+)/(?P<class_id>\d+)", "chat.views.room", name="room"),
    
    # admin type stuff.
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

    url(r'^khanapi/$', 'khanapi.views.index'),
    url(r'^proxy/$', 'khanapi.views.proxy'),
    url(r'^oauth_get_request_token/$', 'khanapi.views.oauth_get_request_token'),
    url(r'^oauth_callback/$', 'khanapi.views.oauth_callback'),
    
    # django socket io
    url("", include("django_socketio.urls")),
)

urlpatterns += staticfiles_urlpatterns()
