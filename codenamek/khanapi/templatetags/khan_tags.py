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

from codenamek.khanapi.khan_api import *

from django import template
register = template.Library()

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

@register.inclusion_tag('khanapi/khan_user_login.html', takes_context = True)
def khan_user_login(context):
    request = context['request']
        
    return { 'khan_user_active': is_khan_user_active(request) }

@register.inclusion_tag('khanapi/khan_user_data.html', takes_context = True)
def khan_user_data(context):
    request = context['request']
    return { 'khan_user_active': is_khan_user_active(request), 'khan_user': get_khan_user(request) }

@register.inclusion_tag('khanapi/khan_exercise.html', takes_context = True)
def khan_exercises(context):
    request = context['request']
    if not is_khan_user_active(request):
        return { 'khan_user_active': is_khan_user_active(request), 'khan_api_exercises':'', 'khan_user': '' }
    return { 'khan_user_active': is_khan_user_active(request), 'khan_api_exercises':get_json_for_khan_api_call(request, '/api/v1/exercises'), 'khan_user': get_khan_user(request) }

@register.inclusion_tag('khanapi/khan_badges.html', takes_context = True)
def khan_badges(context):
    request = context['request']
    if not is_khan_user_active(request):
        return { 'khan_user_active': is_khan_user_active(request), 'khan_badges':'', 'khan_user': '' }
    return { 'khan_user_active': is_khan_user_active(request), 'khan_badges':get_json_for_khan_api_call(request, '/api/v1/badges'), 'khan_user': get_khan_user(request) }

@register.inclusion_tag('khanapi/khan_exercise_history.html', takes_context = True)
def khan_exercise_history(context):
    request = context['request']
    if not is_khan_user_active(request):
        return { 'khan_user_active': is_khan_user_active(request), 'khan_api_exercise_history':'', 'khan_user': ''}
    return { 'khan_user_active': is_khan_user_active(request), 'khan_api_exercise_history':get_json_for_khan_api_call(request, '/api/v1/users/exercises'), 'khan_user': get_khan_user(request)}