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
from codenamek.khanapi.khan_api import *

import os, datetime

    
def create_challenge_exercise(_exercise_name, _url, _challenge):
    challenge_exercise = ChallengeExercise(
                           exercise_name=_exercise_name, 
                           exercise_url=_url, 
                           exercise_description='', 
                           challenge=_challenge)
    
    challenge_exercise.save()
    return challenge_exercise

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
    
    school_class.save()
    
    chatroom_name = "%s: %s" % (existing_school.school_name, school_class.class_name)
    chatroom, created  = ChatRoom.objects.get_or_create(name=chatroom_name)
    
    return school_class

def add_team_to_class(_class_id, _team_name):
    """
    Creates a new and empty team
    """
    existing_class = Classroom.objects.get(id=_class_id)
    team = ClassroomTeam(classroom=existing_class, team_name=_team_name, name='team.class.%s.%s.%s' % (existing_class.name, _team_name, existing_class.school.name))
    team.save()
    return team

def add_user_to_class(user, classroom):
    group = Group.objects.get(id=classroom.id)
    group.user_set.add(user)
    group.save()
    return

def add_user_to_team(user, team):
    group = Group.objects.get(id=team.id)
    group.user_set.add(user)
    group.save()
    return

def get_challenges_for_group(group):
    group_challenges = group.group_challenges
    challenges = []
    for ge in group_challenges:
        challenges.add(ge.challenge)
    
    return challenges

def create_challenge_for_class(_classroom, _challenge_name):
    challenge = Challenge(challenge_name=_challenge_name, classroom=_classroom)
    try:
        challenge.save()
    except e:
        print e
        
    return challenge

def add_team_to_challenge(team, challenge):
    challenge_group = GroupChallenge(classroom_team=team, challenge=challenge)
    challenge_group.save()
    print "Team '%s' given challenge of: %s" % (team, challenge)
    
# Returns True or False by looking at all users in team
def get_exercise_proficiency_for_team(team, exercise_name):
    if team.user_set.all().count() == 0:
        return False
    
    all_members_proficient = False
    i_number_of_proficient_users = 0
    for user in team.user_set.all():
        is_proficient = get_proficiency_for_exercise(user, exercise_name)
        if is_proficient == True:
            i_number_of_proficient_users = i_number_of_proficient_users + 1
    
    return team.user_set.all().count() == i_number_of_proficient_users;

from datetime import datetime
def get_team_proficiency_date_for_exercise(team, exercise_name):
    if team.user_set.all().count() == 0:
        return None
    
    most_recent_proficiency_date = None
    all_members_proficient = False
    i_number_of_proficient_users = 0
    for user in team.user_set.all():
        user_exercise_state = get_proficiency_for_exercise(user, exercise_name)
        if user_exercise_state['proficient'] == 'True' or user_exercise_state['proficient'] == True:
            i_number_of_proficient_users = i_number_of_proficient_users + 1
            # Do not worry, this hits the cache 100% of the time
            pro_date = get_proficiency_date_for_exercise(user, exercise_name)
            converted_date = None
            if pro_date is not None and pro_date != '':
                converted_date = convert_khan_string_to_date(pro_date)
                
            if most_recent_proficiency_date is None:
                most_recent_proficiency_date = converted_date
            else:
                # compare the dates, keep the most recent one
                if coverted_date > most_recent_proficiency_date:
                    most_recent_proficiency_date = converted_date
                print "Converted date is %s" % converted_date
                print "Most recent date is %s" % most_recent_proficiency_date
              
    if most_recent_proficiency_date is None:
        print "WARNING: No proficiency dates were found for any members of the team."
    else:
        if team.user_set.all().count() > i_number_of_proficient_users:
            print "WARNING: Most recent date for proficiency in team was %s, but some users didn't have any proficiency, so no team date is valid yet." % most_recent_proficiency_date
    
    return most_recent_proficiency_date

def get_main_school_for_user(**kwargs):
    """
    Gets the user's default school
    """
    _user = User.objects.get(**kwargs)
    if _user.get_profile().default_school is None:
        schools = School.objects.filter(group_ptr=_user.groups.filter(name__startswith="school."))
        for school in schools:
            _user.get_profile().default_school = school
            _user.get_profile().save()
            return school
    
    elif _user.get_profile().default_school is not None :
        return _user.get_profile().default_school
    
def add_user_to_school(user, school):
    if user.get_profile().default_school is None:
        user.get_profile().default_school = school
        user.get_profile().save()
    
    if user.groups.filter(id=school.id).count() == 0:
        user.groups.add(school)
        user.save()

def create_team_for_tests():
    school = add_school(school_name="Rock School")
    school_class = add_class(school_id=school.id, _class_name="Geology 101")
    team = add_team_to_class(school_class.id, "The Rockettes")
    return team      