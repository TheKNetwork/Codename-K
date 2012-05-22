from django.shortcuts import render_to_response, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.views.decorators.cache import *

import simplejson
import simplejson as json

from whiteboard.models import *
from schools.models import *
from schools.usermanagement_api import *
from schools.schoolmanagement_api import *
from schools.forms import *

from whiteboard.models import *

from oauth.oauth import OAuthConsumer, OAuthToken
import requests
import logging
import uuid

from khanapi.khan_api import *
from khanapi.async import *

from celery.task import Task
from celery.registry import tasks

logger = logging.getLogger('dev')

@login_required
@never_cache
def index(request, user_name):
    return homeroom_failsafe(request)

@login_required
@never_cache
def homeroom_failsafe(request):
    json_objects = ''
    active_khan_user = False
    if request.user.get_profile() is not None:
        if request.user.knet_profile.access_token is not None:
            print "Found Khan API access token for user %s" % request.user
            request.session['oauth_token_string'] = request.user.knet_profile.access_token
            active_khan_user = True
            UpdateUserRelatedInfo.delay(user_id=request.user.id)
    else:
        UserProfile(user = request.user).save() 
               
    main_school = get_main_school_for_user(id=request.user.id)
    teams = get_teams_for_user(id=request.user.id)
    all_schools = School.objects.all()
    classes_not_joined = None
    
    if main_school is not None:
        classes_not_joined = get_classes_not_joined(user_id=request.user.id, school_id=main_school.id)
    
    # GET ALL SCHOOLS >> schools = get_schools_for_user(username=request.user.username)
    
    data = {'user': request.user, 
            'main_school': main_school, 
            'khan_user_active':active_khan_user, 
            'teams':teams,
            'all_schools':all_schools,
            'classes_not_joined': classes_not_joined, }
    
    return render(request, "homeroom/user_home.html", data, context_instance = RequestContext(request))


@login_required
@never_cache
def unfinished_exercises(request, user_name):
    unfinished_exercises, found_any_unfinished = get_unfinished_challenges_for_user(user_id=request.user.id)
    data = {'unfinished_exercises': unfinished_exercises,
            'found_any_unfinished': found_any_unfinished }
    
    return render(request, "schools/unfinished_exercises.html", data, context_instance = RequestContext(request))
    
@login_required
@never_cache
def unfinished_exercises_nocache(request, user_name):
    print "FORCING REFRESH"
    unfinished_exercises, found_any_unfinished = get_unfinished_challenges_for_user(user_id=request.user.id, force_refresh=True)
    data = {'unfinished_exercises': unfinished_exercises,
            'found_any_unfinished': found_any_unfinished }
    
    return render(request, "schools/unfinished_exercises.html", data, context_instance = RequestContext(request))
    
@login_required
@never_cache
def join_school(request, user_name, school_id):
    user = request.user
    school = School.objects.get(id=school_id)
    add_user_to_school(user, school)
    return HttpResponseRedirect('/homeroom')

@login_required
@never_cache
def leave_school(request, user_name, school_id):
    user = request.user
    school = School.objects.get(id=school_id)
    remove_user_from_school(user, school)
    return HttpResponseRedirect('/homeroom')

@login_required
@never_cache
def join_class(request, user_name, school_id, class_id):
    user = request.user
    classroom = Classroom.objects.get(id=class_id)
    add_user_to_class(user, classroom)
    return HttpResponseRedirect('/homeroom')

@login_required
@never_cache
def leave_class(request, user_name, school_id, class_id):
    user = request.user
    classroom = Classroom.objects.get(id=class_id)
    remove_user_from_class(user, classroom)
    return HttpResponseRedirect('/homeroom')

@login_required
@never_cache
def join_team(request, user_name, school_id, class_id, team_id):
    user = request.user
    team = ClassroomTeam.objects.get(id=team_id)
    add_user_to_team(user, team)
    return HttpResponseRedirect('/%s/schools/%s/%s' % (user_name, school_id, class_id))

@login_required
@never_cache
def leave_team(request, user_name, school_id, class_id, team_id):
    user = request.user
    team = ClassroomTeam.objects.get(id=team_id)
    remove_user_from_team(user, team)
    return HttpResponseRedirect('/%s/schools/%s/%s' % (user_name, school_id, class_id))

def team_selection(request, user_name, school_id, class_id):
    schools = get_schools_for_user(id=request.user.id)
    classroom = Classroom.objects.get(id=class_id)
    teams = classroom.teams
    data = {'user': request.user, 'schools': schools, 'school_class':classroom, 'teams':teams }
    return render(request, "schools/team_selection.html", data)

def add_challenge_form(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    teams = classroom.teams
    data = {'user': request.user, 'school': school, 'school_class':classroom, 'teams':teams }
    return render(request, "schools/add_challenge.html", data)

@login_required
@never_cache
def remove_challenge(request, user_name, school_id, class_id, challenge_id):
    remove_challenge_and_exercises(id=challenge_id)
    return HttpResponse("removed")

@login_required
@cache_page(5)
def group_section(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    teams = classroom.teams
    team_pro_count = dict()
    current_team = None

    teams, current_team = refresh_team_info_for_user(user_id=request.user.id, teams=teams)
    
    for team in teams.all():
        for challenge in team.challenges.all():
            print "  %s" % challenge
        
            complete_count = 0
            for exercise in challenge.exercises.all():
                ex_pro = get_exercise_proficiency_for_team(team, exercise.exercise_name)
                print "Exercise %s complete? %s" % (exercise, ex_pro)
                if ex_pro:
                    complete_count = complete_count + 1
        
            print "Challenge exercise complete count: %s" % complete_count
        
        user_ex = []
        for user in team.user_set.all():
            ex_status = {}
            for exercise in challenge.exercises.all():
                ex_status['user'] = user
                ex_status['exercise'] = exercise
                user_ex_pro = get_proficiency_for_exercise(user, exercise.exercise_name)
                ex_status['is_pro'] = user_ex_pro
            user_ex.append(ex_status)
         
    form = ClassroomTeamForm()
    data = {'school':school, 
            'school_class': classroom, 
            'teams':teams,
            'form': form,
            'current_team':current_team }
    
    return render(request, "schools/class_congregation_groups.html", data, 
                  context_instance=RequestContext(request, {}))

@login_required
@never_cache
def challenges(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    teams = classroom.teams
    challenges = classroom.challenges
    
    challenge_form = ChallengeForm()
    data = {'school':school, 
            'school_class': classroom, 
            'challenges': challenges,
            'teams':teams,
            'challenges_form': challenge_form}
    return render(request, "schools/class_challenges.html", data, 
                  context_instance=RequestContext(request, {}))

@login_required
@never_cache
def challenge(request, school_id, class_id, challenge_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    challenge = Challenge.objects.get(id=challenge_id)
    team_statuses = get_team_status_for_challenge(challenge_id=challenge_id)
    
    data = {'school':school, 
            'school_class': classroom, 
            'challenge': challenge, 
            'team_statuses': team_statuses, }
    
    return render(request, "schools/challenge.html", data, 
                  context_instance=RequestContext(request, {}))

@login_required
@never_cache
def challenge_add(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    _classroom = Classroom.objects.get(id=class_id)
    
    teams_to_add_string = request.POST['team_ids']
    team_list = teams_to_add_string.split('^|^')
    
    exercises = request.POST['selected_exercises'].encode('utf-8')
    print "Exercise string from form = %s" % exercises
    
    exercise_json = simplejson.loads(exercises);
    
    form = ChallengeForm(request.POST)
    teams = _classroom.teams
    challenge = None
    
    if form.is_valid(): 
        print "Form is valid"
        challenge = create_challenge_for_class(_classroom, form.cleaned_data['challenge_name'] )
        for team_id in team_list:
            try:
                team_to_add = ClassroomTeam.objects.get(id=team_id)
                add_team_to_challenge(team_to_add, challenge)
                print "Added team %s to challenge" % team_to_add
            except:
                pass
            
        for obj in exercise_json:
            title = obj[0]
            url = obj[1]
            print "Creating exercise challenge for %s" % title
            chex = create_challenge_exercise(title, url, challenge)
               
    else:
        print "Form not valid"
        
    new_form = ChallengeForm()
    challenges = _classroom.challenges
    data = {'school':school, 'school_class': _classroom, 'added_challenge':challenge, 'challenge_form':new_form, 'challenges':challenges, 'teams':teams}    
    return render(request, "schools/class_challenges.html", data, 
                  context_instance=RequestContext(request, {}))

@login_required
@never_cache
def group_add(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    team = None
    form = ClassroomTeamForm(request.POST)

    if form.is_valid(): 
        team = add_team_to_class(classroom.id, form.cleaned_data['team_name'] )
        print "Added %s" % (form.cleaned_data['team_name'])
    else:
        print "Form not valid"
        
    new_form = ClassroomTeamForm()
    data = {'school':school, 'school_class': classroom, 'added_team':team, 'form':new_form}
    return render(request, "schools/class_congregation_groups.html", data, 
                  context_instance=RequestContext(request, {}))

@login_required
@never_cache
def create_a_class(request, _school_id, user_name):
    if request.method == 'POST': # If the form has been submitted...
        form = ClassroomForm(request.POST)
        if form.is_valid(): 
            classroom = add_class(school_id=_school_id, 
                      _class_name=form.cleaned_data['class_name'], 
                      _class_description='' )
            
            add_user_to_class(request.user, classroom)
            print "Added %s" % (form.cleaned_data['class_name'])
            return HttpResponseRedirect('/%s/homeroom/' % user_name) 
    else:
        form = ClassroomForm() # An unbound form

    return render_to_response('schools/add_class.html', {
        'form': form, 'school_id': _school_id,
    }, context_instance=RequestContext(request, {}))

@login_required
@cache_page(5)
def classes_for_school(request, school_id, user_name):
    school = School.objects.get(id=school_id)
    classes = school.classrooms.all()
    data = {'user': request.user, 'school':school, 'classes': classes}
    return render(request, "schools/classes.html", data)

@login_required
@cache_page(5)
def class_congregation(request, school_id, class_id, user_name):
    print "class id %s" % class_id
    school_class = Classroom.objects.get(id=class_id)
    school = School.objects.get(id=school_id)
    whiteboard_sessions = WhiteboardSession.objects.all()
    
    data = {'user': request.user, 'school_class': school_class, 
            'school':school, 'whiteboard_sessions': whiteboard_sessions,}

    return render(request, "schools/class_congregation.html", data)

@login_required
@cache_page(5)
def team(request, school_id, class_id, user_name, team_id):
    print "class id %s" % class_id
    school_class = Classroom.objects.get(id=class_id)
    school = School.objects.get(id=school_id)
    whiteboard_sessions = WhiteboardSession.objects.all()
    team = ClassroomTeam.objects.get(id=team_id)
    challenge_statuses = get_challenge_status_for_team(team_id=team_id)
    
    data = {'user': request.user, 'school_class': school_class, 
            'school':school, 'whiteboard_sessions': whiteboard_sessions,
            'team': team, 'challenge_statuses':challenge_statuses,}

    return render(request, "schools/team.html", data)
