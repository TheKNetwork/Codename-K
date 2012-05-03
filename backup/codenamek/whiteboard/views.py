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

from codenamek.whiteboard import tutor_trove_auth
from codenamek.whiteboard.models import *
from codenamek.whiteboard.forms import *
import time
import os
import base64

import logging
logger = logging.getLogger('dev')

def create_whiteboard(request):
    if request.method == 'POST': # If the form has been submitted...
        form = WhiteboardSessionForm(request.POST)
        if form.is_valid(): 
            user = request.user # get the user from the request
            if user is None:
                user = "anonymous"
                
            user_type = "tutor"
            user_name = user
            user_id = "%s:%s" % (user, os.urandom(30))
            
            title = form.cleaned_data['whiteboard_title']
            hash = base64.urlsafe_b64encode(os.urandom(30))
            
            # generate the whiteboard url for the iframe
            url = tutor_trove_auth.get_whiteboard_url(title, hash, user_type, user_name, user_id)
            whiteboard_session = WhiteboardSession(whiteboard_title=title, whiteboard_hash=hash, whiteboard_url=url)
            whiteboard_session.save()
            
            print "Added %s" % (form.cleaned_data['whiteboard_title'])
            return HttpResponseRedirect('/classroom/%s' % whiteboard_session.id) 

def show_whiteboard(request, whiteboard_id):
    user = request.user # get the user from the request
    if user is None:
        user = "anonymous"
        
    user_type = "tutor"
    user_name = user
    user_id = "%s:%s" % (user, os.urandom(30))
    
    hash = ''
    title = ''
    url = ''
    
    whiteboard_session = WhiteboardSession.objects.get(id=whiteboard_id)
    title = whiteboard_session.whiteboard_title
    hash = whiteboard_session.whiteboard_hash
    url = tutor_trove_auth.get_whiteboard_url(title, hash, user_type, user_name, user_id)
    print "url is %s" % url
    
    # render the html
    return render_to_response("whiteboard/index.html", {'user': request.user, 'whiteboard_url':url})

def index(request):
    """
    Grab some information out of the the request, namely:
        the current user,
        whiteboard_title,
        whiteboard_hash,
        user_type,
        user_name,
        user_id
        
    Use the tutor_trove_auth.py method(s) to generate a valid tutor_trove url and
    put that url in the response. The template html should use this url value
    in the iframe that loads the whiteboard.
    
    NOTE: using the same user_id twice will force any users after the first one
    to show as having the same names.
    """
    user = request.user # get the user from the request
    
    if user is None:
        user = "anonymous"
    
    # get the whiteboard information from the request.
    whiteboard_title = "A Title"
    whiteboard_hash = "wealluseonewhiteboardfornow"
    user_type = "tutor"
    user_name = user
    user_id = user
    
    # generate the whiteboard url for the iframe
    whiteboard_url = tutor_trove_auth.get_whiteboard_url(whiteboard_title, whiteboard_hash, user_type, user_name, user_id)
    
    # render the html
    return render_to_response("whiteboard/index.html", {'user': user, 'whiteboard_url':whiteboard_url})
