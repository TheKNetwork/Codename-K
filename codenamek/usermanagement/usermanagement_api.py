"""
This file is responsible for the logic and db methods to 
manipulate the db objects defined in models.py
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist
import os, datetime

from codenamek.usermanagement.signals import *
from codenamek.usermanagement.models import *

def get_schools_for_user(**kwargs):
    """
    Retrieves a list of schools for a certain user. A school *is* a group,
    so this relies on the built in django auth module
    """
    user = User.objects.get(**kwargs)
    schools = School.objects.filter(group_ptr=user.groups.filter(name__startswith="school."))
    return schools

def invite_user_to_class(inviting_user_id, invited_user_id, school_class_id):
    """
    Creates a ClassInvitation object and relates the proper references to the
    invited user and the user that was invited.
    """
    invited_by = User.objects.get(id=inviting_user_id)
    invited_user = User.objects.get(id=invited_user_id)
    school_class = Classroom.objects.get(id=school_class_id)
    class_invitation = ClassInvitation.objects.create(
                            school_class=school_class,
                            invited_user=invited_user,
                            invited_by=invited_by
                        )
    return class_invitation
    
def invite_user_to_class_by_lookup_names(inviting_user_name, invited_user_name, school_name, school_class_name):
    """
    Allows passing in of user names, school name and a class name and this 
    method finds the records for those lookups and creates an invitation. This
    method is mostly for easy test writing. It is recommended to use the original 
    'invite_user_to_class' method.
    """
    inviter = User.objects.get(username=inviting_user_name)
    invited = User.objects.get(username=invited_user_name)
    school = School.objects.get(school_name=school_name)
    school_class = school.classrooms.filter(class_name=school_class_name)[0]
    return invite_user_to_class(inviter.id, invited.id, school_class.id)
    
def accept_invitation_to_class(current_user, invitation_id):
    """
    Accepts an invitation to a class. This just boils down to setting an accepted date
    on the invitation object.
        
    TODO: This method should also signal an email to both users involved
    so that if any further communication or verification is needed, it is
    more likely to happen.
    """
    existing_invitations = current_user.invitations_received.filter(id=invitation_id)
    for invitation in existing_invitations:
        if invitation.id == invitation_id:
            invitation.accepted_on_date = datetime.datetime.now()
            invitation.save()
            return invitation
        
    raise "No matching invitation found."

def reject_invitation_to_class(current_user, invitation_id):
    """
    Rejects an invitation to a class by setting the reject date.
    
    TODO: This method should also signal an email to both users involved
    so that if any further communication or verification is needed, it is
    more likely to happen.
    """
    existing_invitations = current_user.invitations_received.filter(id=invitation_id)
    for invitation in existing_invitations:
        if invitation.id == invitation_id:
            invitation.rejected_on_date = datetime.datetime.now()
            invitation.save()
            return invitation
        
    raise "No matching invitation found."