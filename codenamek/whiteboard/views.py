from django.shortcuts import render_to_response
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from codenamek.whiteboard import tutor_trove_auth

import logging
logger = logging.getLogger('dev')

@login_required
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
    
    # get the whiteboard information from the request.
    whiteboard_title = "A Title"
    whiteboard_hash = "wealluseonewhiteboardfornow"
    user_type = "tutor"
    user_name = user.get_full_name
    user_id = user.id
    
    # generate the whiteboard url for the iframe
    whiteboard_url = tutor_trove_auth.get_whiteboard_url(whiteboard_title, whiteboard_hash, user_type, user_name, user_id)
    
    # render the html
    return render_to_response("whiteboard/index.html", {'user': user, 'whiteboard_url':whiteboard_url})
