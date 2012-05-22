from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "index.html",
    }, name="home"),
                       
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^announcements/", include("announcements.urls")),
    
    # begin knet added urls
    url(r"^khanapi/", include("khanapi.urls")),
    
    url(r'^challenge/(?P<challenge_id>\d+)/(?P<school_id>\d+)/(?P<class_id>\d+)', 'schools.views.challenge', name='challenge'),
    url(r'^(?P<user_name>\w+)/homeroom/$', 'schools.views.index', name='homeroom_user'),
    url(r'^(?P<user_name>\w+)/unfinished-exercises-nocache/', 'schools.views.unfinished_exercises_nocache', name='unfinished_exercises_nocache'),
    url(r'^(?P<user_name>\w+)/unfinished-exercises/', 'schools.views.unfinished_exercises', name='unfinished_exercises'),
    url(r'^homeroom/$', 'schools.views.homeroom_failsafe', name='homeroom'),
    
    # School related urls
    url(r'^(?P<user_name>\w+)/join_team/(?P<school_id>\d+)/(?P<class_id>\d+)/(?P<team_id>\d+)','schools.views.join_team', name='join_team'), 
    url(r'^(?P<user_name>\w+)/leave_team/(?P<school_id>\d+)/(?P<class_id>\d+)/(?P<team_id>\d+)','schools.views.leave_team', name='leave_team'), 
    
    url(r'^(?P<user_name>\w+)/join_class/(?P<school_id>\d+)/(?P<class_id>\d+)','schools.views.join_class', name='join_class'), 
    url(r'^(?P<user_name>\w+)/leave_class/(?P<school_id>\d+)/(?P<class_id>\d+)','schools.views.leave_class', name='leave_class'), 
    
    url(r'^(?P<user_name>\w+)/join_school/(?P<school_id>\d+)','schools.views.join_school', name='join_school'), 
    url(r'^(?P<user_name>\w+)/leave_school/(?P<school_id>\d+)','schools.views.leave_school', name='leave_school'), 
    
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/team/(?P<team_id>\d+)','schools.views.team', name='team'),
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/team_selection','schools.views.team_selection', name='team_selection'),
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/add_team_to_challenge/(?P<team_id>\d+)/(?P<challenge_id>\d+)','schools.views.add_team_to_challenge', name='add_team_to_challenge'),
    url(r'^(?P<user_name>\w+)/(?P<school_id>\d+)/(?P<class_id>\d+)/add_challenge_form','schools.views.add_challenge_form', name='add_challenge_form'), 
    url(r'^(?P<user_name>\w+)/remove_challenge/(?P<school_id>\d+)/(?P<class_id>\d+)/(?P<challenge_id>\d+)','schools.views.remove_challenge', name='remove_challenge'), 
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/challenges','schools.views.challenges', name='challenges'), 
    url(r'^(?P<user_name>\w+)/schools/(?P<_school_id>\d+)/create_a_class','schools.views.create_a_class'),

    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/challenge_add','schools.views.challenge_add', name='challenge_add'),    

    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/group_add','schools.views.group_add', name='group_add'),    
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/groups','schools.views.group_section', name='group_section'),
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)/(?P<team_id>\d+)','schools.views.team', name='team'),
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)/(?P<class_id>\d+)','schools.views.class_congregation', name='class_congregation'),
    
    url(r'^(?P<user_name>\w+)/schools/(?P<school_id>\d+)','schools.views.classes_for_school', name='schools_class'),
    url(r'^(?P<user_name>\w+)/schools/$', 'schools.views.index', name='schools'),
    
    url(r'^classroom/(?P<whiteboard_id>\d+)/$', 'whiteboard.views.show_whiteboard'),
    url(r'^classroom/create_whiteboard', 'whiteboard.views.create_whiteboard'),
    
    url(r'^khanapi/topic_tree', 'khanapi.views.topic_tree'),
    url(r'^khanapi/$', 'khanapi.views.index'),
    url(r'^khanapi/proxy/$', 'khanapi.views.proxy'),
    url(r'^oauth_get_request_token/$', 'khanapi.views.oauth_get_request_token'),
    url(r'^oauth_callback/$', 'khanapi.views.oauth_callback'),
    url(r'^khanapi/khan_user_info', 'khanapi.views.khan_user_info'),
    
    url(r"^chat/", include("chat.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
