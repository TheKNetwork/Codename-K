# Create your views here.
# from django.shortcuts import redirect
from django.shortcuts import render_to_response
# from django.template import RequestContext
from django.contrib.auth.models import Group, User

import logging
logger = logging.getLogger('dev')

def index(request):
    groupList = Group.objects.all()
    logger.debug('Count of groups: ' + str(groupList.count()))
    
    userList  = User.objects.all()
    logger.debug('Count of users: ' + str(userList.count()))
    
    return render_to_response("user_home.html", {'groups': groupList, 'users': userList} )