from django.shortcuts import render_to_response, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.core.cache import *

from urllib import urlencode
from oauth import OAuthToken
from cStringIO import StringIO

from khanapi.views import *
from khanapi.api_explorer_oauth_client import APIExplorerOAuthClient

import urllib
import urllib2
import string
import time
import cgi, os, sys
import simplejson

MONTH = 60 * 60 * 24 * 30
DAY = 60 * 60 * 24
HALF_A_DAY = 60 * 60 * 12
QUARTER_DAY = 60 * 60 * 6
TYPICAL_SESSION = 60 * 60 * 2
ONE_MINUTE = 60

TOPIC_TREE = ''

# PUBLIC FACING METHODS HERE
def is_khan_user_active(request):
    active_khan_user = False
    if request.user.knet_profile is not None:
        if request.user.knet_profile.access_token is not None:
            request.session['oauth_token_string'] = request.user.knet_profile.access_token
            active_khan_user = True
    return active_khan_user;

def get_khan_user(user, force_refresh=False):
    try:
        return execute_khan_api_method(
                                       user.knet_profile.access_token, 
                                       '/api/v1/user', cache_timeout=DAY,
                                       user_id=user.id,
                                       force_refresh=force_refresh)
    except:
        return ''   

def get_all_khan_exercises(user, force_refresh=False):
    try:
        return execute_khan_api_method(
                                       user.knet_profile.access_token, 
                                       '/api/v1/exercises', 
                                       user_id=user.id, cache_timeout=MONTH,
                                       cache_per_user=False,
                                       force_refresh=force_refresh)
    except:
        return ''  

def get_khan_exercises(user, force_refresh=False):
    try:
        return execute_khan_api_method(user.knet_profile.access_token, 
                                       '/api/v1/user/exercises', user_id=user.id, 
                                       disk_cache=True, cache_timeout=DAY,
                                       cache_per_user=True,
                                       force_refresh=force_refresh)
    except:
        return ''  

def get_khan_badges(user, force_refresh=False):
    try:
        return execute_khan_api_method(
                                       user.knet_profile.access_token, 
                                       '/api/v1/badges', 
                                       user_id=user.id, 
                                       cache_timeout=MONTH,
                                       cache_per_user=False,
                                       force_refresh=force_refresh)
    except:
        return '' 
    
def print_topic(topic):
    print "Topic is %s" % topic['title']
    for item in topic['children']:
        if item['kind'] == "Exercise":
            print "Exercise: %s" % item['display_name']
        elif item['kind'] == "Topic":
            print_topic(item)      
    
def get_khan_topic_tree(user, force_refresh=False):
    try:
        jsondata = execute_khan_api_method(user.knet_profile.access_token,
                                           '/api/v1/topictree',
                                           cache_timeout=MONTH,
                                           cache_per_user=False,
                                           force_refresh=force_refresh)
    except:
        return 'ERROR'
    
    return jsondata
    
def get_khan_playlist_library(user, force_refresh=False):
    try:
        jsondata = execute_khan_api_method(user.knet_profile.access_token, 
                                           '/api/v1/playlists/library', 
                                           user_id=user.id, 
                                           cache_timeout=MONTH,
                                           cache_per_user=False,
                                           force_refresh=force_refresh)
        
        return jsondata
    except:
        return ''     
    
def get_khan_playlist_exercises_for_title(user, playlist_title, force_refresh=False):
    try:
        return execute_khan_api_method(
                                       user.knet_profile.access_token, 
                                       '/api/v1/playlists/%s/exercises' % playlist_title, 
                                       user_id=user.id, 
                                       cache_timeout=MONTH,
                                       cache_per_user=False,
                                       force_refresh=force_refresh)
    except:
        return ''    

def get_khan_exercise_history(user, force_refresh=False):
    return execute_khan_api_method(
                                   user.knet_profile.access_token, 
                                   '/api/v1/exercise_history', 
                                   user_id=user.id,
                                   force_refresh=force_refresh)


from datetime import datetime
# example 2011-08-29T00:00:00Z
def convert_khan_string_to_date(str_date):
    date_object = datetime.strptime(str_date)
    print date_object
    return date_object
    
# Returns a dict of exercise_states{ }
def get_proficiency_for_exercise(user, exercise_name, force_refresh=False):
    default = False
    if user.knet_profile.access_token is None or user.knet_profile.access_token == '':
        return default
    
    jsondata = get_khan_user(user, force_refresh=force_refresh)
    json_friendly_exercise_name = exercise_name.replace(" ","_")
    json_friendly_exercise_name = json_friendly_exercise_name.lower()
    
    try:
        if jsondata is not None:
            for item in jsondata['all_proficient_exercises']:
                if item == json_friendly_exercise_name:
                    return True
    except e:
        print "Got error %s" % e
        
    return default

def get_proficiency_date_for_exercise(user, exercise_name, force_refresh=False):
    exercise_data = get_exercise_for_user(user, exercise_name, force_refresh=force_refresh)
    return exercise_data['proficient_date']

def get_exercise_for_user(user, exercise_name, force_refresh=False):
    return execute_khan_api_method(user.knet_profile.access_token, 
                                   '/api/v1/user/exercises/%s' % exercise_name, 
                                   cache_timeout=HALF_A_DAY,
                                   user_id=user.id,
                                   force_refresh=force_refresh)   


# This method is the funnel point for all khan api calls. It caches data based on
# the user's access token and method passed in.
# The default cache timeout is one hour, 60 seconds * 60 minutes
# Regardless of the cache, a refresh can be forced by passing in force_refresh=True
def execute_khan_api_method(profile_access_token, api_method, cache_timeout=TYPICAL_SESSION, 
                            force_refresh=False, return_raw_text=False, user_id=None, cache_per_user=True,
                            disk_cache=False):
    
    cache_key = ""
    _chosen_cache = None
    if disk_cache == False:
        _chosen_cache = get_cache('default')
    else:
        _chosen_cache = get_cache('disk')
    
    if cache_per_user:
        if user_id is not None:
            cache_key = "%s^%s^%s" % (user_id, api_method, return_raw_text)
        else:
            cache_key = "%s^%s^%s" % (profile_access_token, api_method, return_raw_text)
    else:
        cache_key = "%s^%s" % (api_method, return_raw_text)
    
    cache_key = cache_key.replace("/","^")
    cache_key = cache_key.replace(".","^")
    cache_key = cache_key.replace(":","^")
    cache_key = cache_key.replace(" ","^")
    
    cache_hit = False
    result_data = _chosen_cache.get(cache_key)
    
    if force_refresh or result_data is None:
        
        resource = settings.CLIENT.access_api_resource(
            api_method,
            access_token = OAuthToken.from_string(profile_access_token),
            method = "GET"
            )
        
        text =  resource['body']
        # Error messages can contain HTML. Escape them so they're not rendered.
        is_html = has_text_html_header(resource['headers'])
        if is_html:
            text = cgi.escape(text)
        
        try:
            if return_raw_text:
                result_data = text
            else:
                result_data = simplejson.loads(text)
                
            _chosen_cache.set(cache_key, result_data, cache_timeout)
            test_result = _chosen_cache.get(cache_key)
            if test_result is None:
                print "WHOA - storing in cache didn't do jack squat!!"
                print "   cache key: %s" % cache_key
                print
                print 
        except:
            print "exception storing in cache"
        
    else:
        # print "Got json data from cache!"
        cache_hit = True
    
    if not cache_hit:
        # update local tables with fresh data
        print "(cache not hit or is empty: Update local tables with data)"
    
    return result_data

def has_request_token(session):
    return 'request_token' in session

def has_access_token(session):
    return 'oauth_token_string' in session

def is_connected(session):
    return has_request_token(session) and has_access_token(session)
    
def access_token(session):
    try:
        token_string = session['oauth_token_string']
    except KeyError:
        print 'Got key error'
        token_string = None

    # Sanity check.
    if not token_string:
        print 'Not token string'
        clear_session(session)
        return None
        
    oauth_token = OAuthToken.from_string(token_string)
    print 'Oauth token %s' % oauth_token
    return oauth_token
    
def clear_session(session):
    session.pop('request_token', None)
    session.pop('oauth_token_string', None)

# Expects an array of headers. Figures out if the `Content-Type` is
# `text/html`.
def has_text_html_header(headers):
    for header in headers:
        if (string.find(header, 'Content-Type') > -1 and 
            string.find(header, 'text/html') > -1):
            return True
    return False

def current_site_url():
    from django.contrib.sites.models import Site
    url = 'http://%s' % settings.SITE_ROOT
    return url