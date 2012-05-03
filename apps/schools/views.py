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
            
    whiteboard_sessions = WhiteboardSession.objects.all()
    main_school = get_main_school_for_user(id=request.user.id)
    teams = get_teams_for_user(id=request.user.id)
    all_schools = School.objects.all()
    # GET ALL SCHOOLS >> schools = get_schools_for_user(username=request.user.username)
    
    data = {'user': request.user, 
            'main_school': main_school, 
            'khan_user_active':active_khan_user, 
            'teams':teams,
            'all_schools':all_schools,
            'whiteboard_sessions': whiteboard_sessions}
    
    return render(request, "homeroom/user_home.html", data, context_instance = RequestContext(request))

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
def group_section(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    teams = classroom.teams
    team_pro_count = dict()
    
    for team in teams.all():
        challenge_pro = 0
        exercises_completed = 0
        for challenge in team.challenges.all():
            exercise_total = 0
            exercise_pro = 0
            for exercise in challenge.exercises.all():
                is_pro = get_exercise_proficiency_for_team(team, exercise.exercise_name)
                if is_pro:
                    exercise_pro = exercise_pro + 1
                    exercises_completed = exercises_completed + 1
                exercise_total = exercise_total + 1
            if exercise_total == exercise_pro and exercise_total > 0:
                challenge_pro = challenge_pro + 1
        team.challenge_complete_count = challenge_pro
        team.exercise_complete_count = exercises_completed
        team.save()
         
    form = ClassroomTeamForm()
    data = {'school':school, 
            'school_class': classroom, 
            'teams':teams,
            'form': form}
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
@never_cache
def classes_for_school(request, school_id, user_name):
    school = School.objects.get(id=school_id)
    classes = school.classrooms.all()
    data = {'user': request.user, 'school':school, 'classes': classes}
    return render(request, "schools/classes.html", data)

@login_required
@never_cache
def class_congregation(request, school_id, class_id, user_name):
    school_class = Classroom.objects.get(id=class_id)
    school = School.objects.get(id=school_id)
    whiteboard_sessions = WhiteboardSession.objects.all()
    data = {'user': request.user, 'school_class': school_class, 'school':school, 'whiteboard_sessions': whiteboard_sessions}

    return render(request, "schools/class_congregation.html", data)
