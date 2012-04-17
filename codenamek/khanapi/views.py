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

from api_explorer_oauth_client import APIExplorerOAuthClient
from oauth import OAuthToken

import urllib
from urllib import urlencode
import urllib2
import string
import time
import cgi, os, sys

def index(request):
    data = { 'has_access_token':has_access_token(request.session) }
    return render(request, "khanapi/index.html", data)

# Given a URL, makes a proxied request for an API resource and returns the
# response.
def proxy(request):
    print 'In proxy'
    url = request.GET['url']
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
    
    response = HttpResponse(text)
    # Include the original headers and status as custom response headers. The
    # client side will know what to do with these.
    response.__setitem__('X-Original-Headers', urllib.quote("".join(resource['headers'])))
    response.__setitem__('X-Original-Status',resource['status'])
    
    if is_html:
        response.__setitem__('Content-Type','text/html')
    else:
        response.__setitem__('Content-Type','application/json')
    
    return response
        
# Begin the process of getting a request token from Khan.
# @app.route('/oauth_get_request_token')
def oauth_get_request_token(request):
    print "getting request token"
    callback_url = '%s/oauth_callback' % current_site_url()
    print "callback url is %s" % callback_url
    request_token_url = CLIENT.url_for_request_token(
            callback = callback_url
            )
    print "Redirecting to request token URL: \n%s" % (request_token_url)
    return HttpResponseRedirect(request_token_url)

# The OAuth approval flow finishes here.
# @app.route('/oauth_callback')
def oauth_callback(request):
    print 'In oauth_callback'
    oauth_token    = request.GET['oauth_token']
    oauth_secret   = request.GET['oauth_token_secret']
    oauth_verifier = request.GET['oauth_verifier']

    request_token = OAuthToken(oauth_token, oauth_secret)
    request_token.set_verifier(oauth_verifier)
    
    request.session['request_token']  = request_token
    
    # We do this before we redirect so that there's no "limbo" state where the
    # user has a request token but no access token.
    access_token = CLIENT.fetch_access_token(request_token)
    request.session['oauth_token_string'] = access_token.to_string()
    print "Access token is %s" % access_token.to_string()
    
    profile = request.user.get_profile()
    profile.access_token = access_token.to_string()
    profile.save()

    print "Your account has been associated with Khan Academy username %s" % access_token.to_string()

    # We're done authenticating, and the credentials are now stored in the
    # session. We can redirect back home.
    return HttpResponseRedirect('/khanapi')


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