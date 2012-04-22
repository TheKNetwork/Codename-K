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
import simplejson as json

from codenamek.usermanagement.models import *
from codenamek.usermanagement.usermanagement_api import *
from codenamek.schools.schoolmanagement_api import *
from codenamek.whiteboard.models import *

from oauth.oauth import OAuthConsumer, OAuthToken
import requests
import logging
import uuid

from codenamek.khanapi.khan_api import *

logger = logging.getLogger('dev')

@login_required
@never_cache
def index(request, user_name):
    return homeroom_failsafe(request)

@login_required
@never_cache
def homeroom_failsafe(request):
    json_objects = ''
    active_khan_user = False
    if request.user.get_profile() is not None:
        if request.user.get_profile().access_token is not None:
            print "Found Khan API access token for user %s" % request.user
            request.session['oauth_token_string'] = request.user.get_profile().access_token
            khan_user_info = get_data_for_khan_api_call(request, '/api/v1/user')
            active_khan_user = True
            
    whiteboard_sessions = WhiteboardSession.objects.all()
    main_school = get_main_school_for_user(id=request.user.id)
    # GET ALL SCHOOLS >> schools = get_schools_for_user(username=request.user.username)
    
    data = {'user': request.user, 'main_school': main_school, 'khan_user_active':active_khan_user, 'whiteboard_sessions':whiteboard_sessions }
    
    return render(request, "homeroom/user_home.html", data, context_instance = RequestContext(request))

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

