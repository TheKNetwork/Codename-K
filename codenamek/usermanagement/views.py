from django.shortcuts import render_to_response, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.sites.models import Site

from oauth.oauth import OAuthConsumer, OAuthToken
import requests
import logging

from api_explorer import APIExplorerOAuthClient

logger = logging.getLogger('dev')

server_url = getattr(settings, 'KHAN_URL', "http://www.khanacademy.org")
consumer_key = getattr(settings, 'CONSUMER_KEY', None)
consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
callback = "http://%s%s" % (Site.objects.get_current(), '/khan-academy/auth/callback/')


@login_required
def index(request):
    groupList = Group.objects.all()
    logger.debug('Count of groups: ' + str(groupList.count()))
    
    userList  = User.objects.all()
    logger.debug('Count of users: ' + str(userList.count()))
    
    data = {'user': request.user, 'groups': groupList, 'users': userList}
    return render(request, "homeroom/user_home.html", data)


CLIENT = APIExplorerOAuthClient(server_url,
        consumer_key,
        consumer_secret
        )


@login_required
def request_token(request):
    '''
        Getting request token
    '''
    request_token_url = CLIENT.url_for_request_token(
                callback = callback
                )
    return HttpResponseRedirect(request_token_url)


@login_required
def access_token(request):
    '''
        Getting an access token
    '''
    try:
        oauth_token = request.GET['oauth_token'].encode('ascii')
        oauth_token_secret = request.GET['oauth_token_secret'].encode('ascii')
        oauth_verifier = request.GET['oauth_verifier'].encode('ascii')
    except:
        return HttpResponseBadRequest('Bad request')
    else:
        request_token = OAuthToken(oauth_token, oauth_token_secret)
    request_token.set_verifier(oauth_verifier)
    access_token = CLIENT.fetch_access_token(request_token)
    profile = request.user.get_profile()
    profile.access_token = access_token.to_string()
    profile.save()

    messages.info(request, "Your account have beed associated with Khan Academy usernamer %s" % access_token.to_string())
    return HttpResponseRedirect(reverse('homeroom'))


@login_required
def khan_api_test(request):
    '''
        Simple example of using Khan Academy API
    '''
    #TODO, extend it using requests lib
    #TODO, add decorator for api calls to ensure that we have access_token for user
    #TODO, check 401 status codes in case of any failure
    if not request.user.get_profile().access_token:
        return HttpResponseRedirect(reverse('request-token'))
    access_token = OAuthToken.from_string(request.user.get_profile().access_token.encode('ascii'))
    resource = CLIENT.access_api_resource(
        "/api/v1/user",
        access_token,
        method = "GET"
        )
    return HttpResponse(resource['body'])
