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

# PUBLIC FACING METHODS HERE
def is_khan_user_active(request):
    active_khan_user = False
    if request.user.get_profile() is not None:
        if request.user.get_profile().access_token is not None:
            print "Found Khan API access token for user %s" % request.user
            request.session['oauth_token_string'] = request.user.get_profile().access_token
            active_khan_user = True
    return active_khan_user;

def get_khan_user(request):
    if not is_khan_user_active(request):
        return ''
    return get_json_for_khan_api_call(request, '/api/v1/user')   

def get_khan_exercises(request):
    if not is_khan_user_active(request):
        return ''
    return get_json_for_khan_api_call(request, '/api/v1/exercises')  

def get_khan_badges(request):
    if not is_khan_user_active(request):
        return ''
    return get_json_for_khan_api_call(request, '/api/v1/badges') 

def get_khan_exercise_history(request):
    if not is_khan_user_active(request):
        return ''
    return get_json_for_khan_api_call(request, '/api/v1/exercise_history') 


# UTILITY METHODS, USED BY THE PUBLIC FACING METHODS ABOVE
def get_data_for_khan_api_call(request, url):
    
    print "Got request for url: %s" % url
    
    if not url:
        abort(400)

    # Returns a dictionary with keys: 'headers', 'body', and 'status'.
    resource = CLIENT.access_api_resource(
        url,
        access_token(request.session),
        method = request.method
        )
    
    text = resource['body']

    # Error messages can contain HTML. Escape them so they're not rendered.
    is_html = has_text_html_header(resource['headers'])
    if is_html:
        text = cgi.escape(text)
    
    return text

def get_json_for_khan_api_call(request, url):
    text = get_data_for_khan_api_call(request, url)
    try:
        jsondata = simplejson.loads(text)
    except:
        jsondata = ''
        
    return jsondata

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