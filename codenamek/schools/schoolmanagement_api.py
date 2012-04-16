"""
This file is responsible for the logic and db methods to 
manipulate the db objects defined in models.py
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist

from codenamek.usermanagement.models import *
from codenamek.schools.models import *

import os, datetime

def add_school(**kwargs):
    """
    Adds a school using the expected arguments for a school object.
    """
    school = School.objects.create(**kwargs)
    school.name = 'school.%s' % school.school_name
    school.save()
    return school

def add_class(school_id, **kwargs):
    """
    Finds a school with the given school id, then creates a class and adds
    the class to that school using the expected arguments for the class
    object type.
    """
    existing_school = School.objects.get(id=school_id)
    school_class = Classroom.objects.create(school=existing_school, **kwargs)
    school_class.name = 'class.%s.%s' % (existing_school.school_name, school_class.class_name)
    school_class.save()
    
    chatroom_name = "%s: %s" % (existing_school.school_name, school_class.class_name)
    chatroom, created  = ChatRoom.objects.get_or_create(name=chatroom_name)
    print "Url for chatroom (slug) is %s" % chatroom.slug
    
    return school_class

def add_user_to_class(user, classroom):
    group = Group.objects.get(id=classroom.id)
    group.user_set.add(user)
    group.save()
    return

def get_main_school_for_user(**kwargs):
    """
    Gets the user's default school
    """
    _user = User.objects.get(**kwargs)
    schools = School.objects.filter(group_ptr=_user.groups.filter(name__startswith="school."))
    count_of = 0
    try:
        count_of = UserDefaultSchool.objects.filter(user__id=_user.id).count()
    except UserProfile.DoesNotExist:
        # user_default_school = UserDefaultSchool(user=_user, main_school=)
        # do nothing
        print "Not found"
    
    if count_of == 1:
        user_school = UserDefaultSchool.objects.get(user__id=_user.id)
        return user_school
    elif count_of == 0:
        for school in schools:
            print "No default school was set, setting default to first school in user's list: %s" % school
            UserDefaultSchool(user=_user, main_school=school)
            return school