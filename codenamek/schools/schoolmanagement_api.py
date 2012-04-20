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
from codenamek.chat.models import *

import os, datetime

def add_school(**kwargs):
    """
    Adds a school using the expected arguments for a school object.
    """
    school = School.objects.create(**kwargs)
    school.name = 'school.%s' % school.school_name
    school.save()
    return school

def add_class(school_id, _class_name, _class_description=''):
    """
    Finds a school with the given school id, then creates a class and adds
    the class to that school using the expected arguments for the class
    object type.
    """
    existing_school = School.objects.get(id=school_id)
    school_class = Classroom.objects.create(school=existing_school, 
                                            class_name=_class_name, 
                                            class_description=_class_description, 
                                            name='class.%s.%s' % (existing_school.school_name, _class_name))
    
    print "************ %s" % school_class.name
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
    if _user.get_profile().default_school is None:
        schools = School.objects.filter(group_ptr=_user.groups.filter(name__startswith="school."))
        print "count of schools found %s" % schools.count()
        for school in schools:
            _user.get_profile().default_school = school
            _user.get_profile().save()
            return school
    
    elif _user.get_profile().default_school is not None :
        return _user.get_profile().default_school
    
    