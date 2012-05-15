from celery.task import Task
from celery.registry import tasks

from whiteboard.models import *
from schools.models import *
from schools.usermanagement_api import *
from schools.schoolmanagement_api import *
from schools.forms import *

class UpdateUserRelatedInfo(Task):

    def run(self, user_id, **kwargs):
        update_user(user_id=user_id)

class UpdateAllUsersRelatedInfo(Task):

    def run(self, **kwargs):
        users = User.objects.all()
        for u in users:
            update_user(user_id=u.id)

def update_user(user_id):
    try:    
        user = User.objects.get(id=user_id)
        school = user.knet_profile.default_school
        print school
        
        classrooms = school.classrooms
        for classroom in classrooms.all():
            teams = classroom.teams
            refresh_team_info_for_user(user_id=user_id, teams=teams)
        
        print "Background task to cache information related to %s is complete." % user

    except Exception, e:
        print e

tasks.register(UpdateUserRelatedInfo)
tasks.register(UpdateAllUsersRelatedInfo)