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

def khan_user_data(context):
    request = context['request']
    print "INCLUDING TAG LIBRARY"
    return { 'khan_user': get_json_for_khan_api_call(request, '/api/v1/user')}

register.inclusion_tag('khanapi/khan_user_data.html', takes_context = True)(khan_user_data)

@register.inclusion_tag('khan_exercise.html')
def get_exercise(request):
    return { 'khan_api_exercises':get_data_for_khan_api_call(request, '/api/v1/exercises') }

@register.inclusion_tag('khan_badges.html')
def get_badges(request):
    return { 'khan_api_exercises':get_data_for_khan_api_call(request, '/api/v1/badges') }

@register.inclusion_tag('khan_exercise_history.html')
def get_user_exercise_history(request):
    return { 'khan_api_exercise_history':get_data_for_khan_api_call(request, '/api/v1/users/exercises')}