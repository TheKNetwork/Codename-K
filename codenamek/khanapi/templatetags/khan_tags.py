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

@register.inclusion_tag('khanapi/khan_user_login.html', takes_context = True)
def khan_user_login(context):
    request = context['request']
    return { 'khan_user_active': is_khan_user_active(request) }

@register.inclusion_tag('khanapi/khan_user_data.html', takes_context = True)
def khan_user_data(context):
    request = context['request']
    return { 'khan_user_active': is_khan_user_active(request), 'khan_user': get_khan_user(request.user) }

@register.inclusion_tag('khanapi/khan_exercise.html', takes_context = True)
def khan_exercises(context):
    request = context['request']
    return { 'khan_user_active': is_khan_user_active(request), 
            'khan_exercises': get_khan_exercises(request.user), 
            'khan_user': get_khan_user(request.user) }

@register.inclusion_tag('khanapi/khan_badges.html', takes_context = True)
def khan_badges(context):
    request = context['request']
    return { 'khan_user_active': is_khan_user_active(request), 
            'khan_badges': get_khan_badges(request.user), 
            'khan_user': get_khan_user(request.user) }

@register.inclusion_tag('khanapi/khan_exercise_history.html', takes_context = True)
def khan_exercise_history(context):
    request = context['request']
    return { 'khan_user_active': is_khan_user_active(request), 
            'khan_exercise_history': get_khan_exercise_history(request.user), 
            'khan_user': get_khan_user(request.user)}