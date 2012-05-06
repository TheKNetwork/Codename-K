from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r'^topic_tree/$', 'khanapi.views.topic_tree'),
    url(r'^js_topic_tree/$', 'khanapi.views.topic_tree_javascript'),
    url(r'^$', 'khanapi.views.index'),
    url(r'^proxy/$', 'khanapi.views.proxy'),
    url(r'^oauth_get_request_token/$', 'khanapi.views.oauth_get_request_token'),
    url(r'^oauth_callback/$', 'khanapi.views.oauth_callback'),
    url(r'^khan_user_info', 'khanapi.views.khan_user_info'),
)
