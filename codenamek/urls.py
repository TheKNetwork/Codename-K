from django.conf.urls.defaults import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout
from codenamek.usermanagement.forms import ProfileForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout),
    url(r'^homeroom/$', 'codenamek.usermanagement.views.index'),
    url(r'^class/session/$', 'codenamek.whiteboard.views.index'),
    url(r'^accounts/', include('registration.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # CAUTION - These next two lines MUST be in the correct order
    ('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),    # 1
    (r'^profiles/', include('profiles.urls')),                                          # 2
)

urlpatterns += staticfiles_urlpatterns()
