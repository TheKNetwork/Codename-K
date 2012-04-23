from django.shortcuts import render_to_response, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template import RequestContext
from codenamek.settings import *
from views import *

from api_explorer_oauth_client import APIExplorerOAuthClient
from oauth import OAuthToken

import urllib
from urllib import urlencode
import urllib2
import string
import time
import cgi, os, sys
import simplejson

from django.core.cache import *

# PUBLIC FACING METHODS HERE
def is_khan_user_active(request):
    active_khan_user = False
    if request.user.get_profile() is not None:
        if request.user.get_profile().access_token is not None:
            request.session['oauth_token_string'] = request.user.get_profile().access_token
            active_khan_user = True
    return active_khan_user;

def get_khan_user(user):
    try:
        return execute_khan_api_method(user.get_profile().access_token, '/api/v1/user', user_id=user.id)
    except:
        return ''   

def get_khan_exercises(user):
    try:
        return execute_khan_api_method(user.get_profile().access_token, '/api/v1/exercises', user_id=user.id)
    except:
        return ''  

def get_khan_badges(user):
    try:
        return execute_khan_api_method(user.get_profile().access_token, '/api/v1/badges', user_id=user.id, disk_cache=True)
    except:
        return '' 
    
def get_khan_playlist_library(user):
    print "Calling library playlist with user id %s" % user.id
    try:
        return execute_khan_api_method(user.get_profile().access_token, '/api/v1/playlists/library', user_id=user.id, disk_cache=True)
    except:
        return ''     

def get_khan_exercise_history(user):
    return execute_khan_api_method(user.get_profile().access_token, '/api/v1/exercise_history', user_id=user.id, disk_cache=True)

from datetime import datetime
# example 2011-08-29T00:00:00Z
def convert_khan_string_to_date(str_date):
    date_object = datetime.strptime(str_date)
    print date_object
    return date_object
    
# Returns a dict of exercise_states{ }
def get_proficiency_for_exercise(user, exercise_name):
    if user.get_profile().access_token is None or user.get_profile().access_token == '':
        print "WARNING: There is no khan user associated with %s" % user
        return { 'proficient':False, 'struggling':False}
    
    jsondata = execute_khan_api_method(user.get_profile().access_token, '/api/v1/user/exercises/%s' % exercise_name, user_id=user.id)  
    if jsondata is not None:
        return jsondata['exercise_states']
    else:
        return { 'proficient':False, 'struggling':False}

def get_proficiency_date_for_exercise(user, exercise_name):
    exercise_data = get_exercise_for_user(user, exercise_name)
    return exercise_data['proficient_date']

def get_exercise_for_user(user, exercise_name):
    return execute_khan_api_method(user.get_profile().access_token, '/api/v1/user/exercises/%s' % exercise_name, user_id=user.id)   

# This method is the funnel point for all khan api calls. It caches data based on
# the user's access token and method passed in.
# The default cache timeout is one hour, 60 seconds * 60 minutes
# Regardless of the cache, a refresh can be forced by passing in force_refresh=True
def execute_khan_api_method(profile_access_token, api_method, cache_timeout=3600, force_refresh=False, return_raw_text=False, user_id=None, disk_cache=False):
    cache_key = ""
    
    _chosen_cache = get_cache('default')
    if disk_cache:
        _chosen_cache = get_cache('disk')
        cache_timeout=(60 * 60 * 24)
    
    if user_id is not None:
        cache_key = "%s:%s:%s" % (user_id, api_method, return_raw_text)
    else:
        cache_key = "%s:%s:%s" % (profile_access_token, api_method, return_raw_text)
    
    cache_hit = False
    result_data = _chosen_cache.get(cache_key)
    
    if result_data is None or result_data == '' or force_refresh:
        resource = CLIENT.access_api_resource(
            api_method,
            access_token = OAuthToken.from_string(profile_access_token),
            method = "GET"
            )
        
        text = resource['body']
        
        # Error messages can contain HTML. Escape them so they're not rendered.
        is_html = has_text_html_header(resource['headers'])
        if is_html:
            text = cgi.escape(text)
        
        try:
            if return_raw_text:
                result_data = text
            else:
                result_data = simplejson.loads(text)
        except:
            result_data = ''
        
        print "Setting cache key:%s to result:%s" % (cache_key, result_data)
        _chosen_cache.set(cache_key, result_data, cache_timeout)
    else:
        print "Got json data from cache!"
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
    url = 'http://%s' % SITE_ROOT
    return url