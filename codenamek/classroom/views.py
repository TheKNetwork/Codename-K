from django.shortcuts import render_to_response
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger('dev')

@login_required
def index(request):
    groupList = Group.objects.all()
    logger.debug('Count of groups: ' + str(groupList.count()))
    
    userList  = User.objects.all()
    logger.debug('Count of users: ' + str(userList.count()))
    
    return render_to_response("homeroom/user_home.html", {'user': request.user, 'groups': groupList, 'users': userList} )