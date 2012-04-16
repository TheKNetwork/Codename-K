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

from codenamek.usermanagement.models import *
from codenamek.usermanagement.usermanagement_api import *
from codenamek.schools.schoolmanagement_api import *

from oauth.oauth import OAuthConsumer, OAuthToken
import requests
import logging
import uuid

from api_explorer import APIExplorerOAuthClient

logger = logging.getLogger('dev')

server_url = getattr(settings, 'KHAN_URL', "http://www.khanacademy.org")
consumer_key = getattr(settings, 'CONSUMER_KEY', None)
consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
callback = "http://%s%s" % (Site.objects.get_current(), '/khan-academy/auth/callback/')

@login_required
def index(request, user_name):
    main_school = get_main_school_for_user(id=request.user.id)
    # GET ALL SCHOOLS >> schools = get_schools_for_user(username=request.user.username)
    data = {'user': request.user, 'main_school': main_school}
    
    return render(request, "homeroom/user_home.html", data)

@login_required
def homeroom_failsafe(request):
    main_school = get_main_school_for_user(id=request.user.id)
    # GET ALL SCHOOLS >> schools = get_schools_for_user(username=request.user.username)
    data = {'user': request.user, 'main_school': main_school}
    
    return render(request, "homeroom/user_home.html", data)

CLIENT = APIExplorerOAuthClient(server_url,
        consumer_key,
        consumer_secret
        )

def activate(request, backend,
     template_name='registration/activate.html',
     success_url=None, extra_context=None, **kwargs):
     backend = get_backend(backend)
     account = backend.activate(request, **kwargs)

     if account:
         request.session['account'] = account
     else:
         account = request.session.get('account', False)

     if not account:
         #TODO, redirect to error page + some messages
         return HttpResponseRedirect('/')
     if request.method == "POST":
         form = PasswordForm(request.POST)
         #assert False
         if form.is_valid():
             password = form.cleaned_data['password']
             account.set_password(password)
             account.save()
             del request.session['account']
             print "Password was udpated"
             return HttpResponseRedirect('/')
     else:
         form = PasswordForm()

     if extra_context is None:
         extra_context = {}
     context = RequestContext(request)
     for key, value in extra_context.items():
         context[key] = callable(value) and value() or value
     context['account'] = 1
     context['form'] = form
     return render_to_response(template_name,
                               kwargs,
                               context_instance=context)


def register(
    request, backend, success_url='/accounts/register/complete/', form_class=None,
    disallowed_url='registration_disallowed',
    template_name='registration/registration_form.html',
    extra_context=None):

    backend = get_backend(backend)
    # if not backend.registration_allowed(request):
    #     return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = backend.register(request, **form.cleaned_data)
            if success_url is None:
                to, args, kwargs = backend.post_registration_redirect(request, new_user)
                redirect_to = reverse(to, *args, **kwargs)
            else:
                redirect_to = success_url
                return HttpResponseRedirect(redirect_to)
    else:
        form = form_class()

    context = {'form': form}
    context.update(extra_context or {})
    return render(request, template_name, context)


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
