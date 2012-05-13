"""
This file is responsible for the logic and db methods to 
manipulate the db objects defined in models.py
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist

from usermanagement_api import *
from schools.models import *
from chat.models import *
from khanapi.khan_api import *

import os, datetime

    
def create_challenge_exercise(_exercise_name, _url, _challenge):
    challenge_exercise = ChallengeExercise(
                           exercise_name=_exercise_name, 
                           exercise_url=_url, 
                           exercise_description='', 
                           challenge=_challenge)
    
    challenge_exercise.save()
    return challenge_exercise


def get_unfinished_challenges_for_user(user_id, force_refresh=False):
    user = User.objects.get(id=user_id)
    teams = get_teams_for_user(id=user_id)
    unfinished_exercises = []
    found_any_unfinished = False
    print "Forcing refresh? %s" % force_refresh
    
    for team in teams:
        challenges = team.challenges.all()
        for challenge in challenges:
            exercises = challenge.exercises.all()
            for exercise in exercises:
                is_pro = get_proficiency_for_exercise(user, exercise.exercise_name, force_refresh)
                if force_refresh:
                    force_refresh = False
                    
                print "User is a pro at %s? ... %s" % (exercise, is_pro)
                if not is_pro:
                    unfinished_exercises.append(exercise)
                    found_any_unfinished = True
    
    return unfinished_exercises, found_any_unfinished

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

def remove_user_from_class(user, classroom):
    group = Group.objects.get(id=classroom.id)
    group.user_set.remove(user)
    group.save()
    return

def add_user_to_team(user, team):
    group = Group.objects.get(id=team.id)
    group.user_set.add(user)
    group.save()
    return

def remove_user_from_team(user, team):
    group = Group.objects.get(id=team.id)
    group.user_set.remove(user)
    group.save()
    return

def get_challenges_for_group(group):
    group_challenges = group.group_challenges
    challenges = []
    for ge in group_challenges:
        challenges.add(ge.challenge)
    
    return challenges

def get_team_status_for_challenge(challenge_id):
    challenge = Challenge.objects.get(id=1)
    teams = []
    for team in challenge.teams.all():
        team_entry = dict()
        team_entry['team'] = team
        exercise_entries = []
        for exercise in challenge.exercises.all():
            team_exercise_entry = dict()
            is_pro = get_exercise_proficiency_for_team(team=team, exercise_name=exercise.exercise_name)
            team_exercise_entry = {'exercise':exercise, 'is_pro': is_pro,}
            
            user_entries = []
            for user in team.user_set.all():
                user_is_pro = get_proficiency_for_exercise(user=user, exercise_name=exercise.exercise_name)
                user_entry = {'user':user, 'is_pro':user_is_pro,}
                user_entries.append(user_entry)
                
            team_exercise_entry['users'] = user_entries
            exercise_entries.append(team_exercise_entry)
        team_entry['exercises'] = exercise_entries
        teams.append(team_entry)
    
    return teams

def create_challenge_for_class(_classroom, _challenge_name):
    challenge = Challenge(challenge_name=_challenge_name, classroom=_classroom)
    try:
        challenge.save()
    except e:
        print e
        
    return challenge

def remove_challenge_and_exercises(**kwargs):
    challenge = Challenge.objects.get(**kwargs)
    for ex in challenge.exercises.all():
        ex.delete()
    
    challenge.delete()

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

def refresh_team_info_for_user(user_id, teams):
        
    for team in teams.all():
        challenge_pro = 0
        exercises_completed = 0
        
        for u in team.user_set.all():
            if u.id == user_id:
                current_team = team
                print "Found current team"
        
        for challenge in team.challenges.all():
            exercise_total = 0
            exercise_pro = 0
            for exercise in challenge.exercises.all():
                is_pro = get_exercise_proficiency_for_team(team, exercise.exercise_name)
                print "Got team proficiency"
                if is_pro:
                    exercise_pro = exercise_pro + 1
                    exercises_completed = exercises_completed + 1
                exercise_total = exercise_total + 1
            if exercise_total == exercise_pro and exercise_total > 0:
                challenge_pro = challenge_pro + 1
        team.challenge_complete_count = challenge_pro
        team.exercise_complete_count = exercises_completed
        team.save()
    return teams, current_team

def get_main_school_for_user(**kwargs):
    """
    Gets the user's default school
    """
    _user = User.objects.get(**kwargs)
    if _user.knet_profile.default_school is None:
        schools = School.objects.filter(group_ptr=_user.groups.filter(name__startswith="school."))
        for school in schools:
            _user.knet_profile.default_school = school
            _user.knet_profile.save()
            return school
    
    elif _user.knet_profile.default_school is not None :
        return _user.knet_profile.default_school
    
def add_user_to_school(user, school):
    if user.knet_profile.default_school is None:
        user.knet_profile.default_school = school
        user.knet_profile.save()
    
    if user.groups.filter(id=school.id).count() == 0:
        user.groups.add(school)
        user.save()

def remove_user_from_school(user, school):
    if user.knet_profile.default_school is not None:
        if user.knet_profile.default_school.id == school.id:
            user.knet_profile.default_school = None
            user.knet_profile.save()
    
    user.groups.remove(school)
    user.save()

def create_team_for_tests():
    school = add_school(school_name="Rock School")
    school_class = add_class(school_id=school.id, _class_name="Geology 101")
    team = add_team_to_class(school_class.id, "The Rockettes")
    return team      