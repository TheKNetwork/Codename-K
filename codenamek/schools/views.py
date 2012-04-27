from django.shortcuts import render_to_response, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template import RequestContext

from codenamek.usermanagement.models import *
from codenamek.usermanagement.usermanagement_api import *
from codenamek.schools.models import *
from codenamek.schools.schoolmanagement_api import *
from codenamek.schools.forms import *
from codenamek.whiteboard.models import *
from django.views.decorators.cache import *
import simplejson

@login_required
@never_cache
def index(request, user_name):
    schools = get_schools_for_user(id=request.user.id)
    data = {'user': request.user, 'schools': schools}
    return render(request, "schools/schools.html", data)

@login_required
@never_cache
def group_section(request, user_name, school_id, class_id):
    school = School.objects.get(id=school_id)
    classroom = Classroom.objects.get(id=class_id)
    teams = classroom.teams
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
            print "Created excercise/challenge object successfully"
               
    else:
        print "Form not valid"
        
    new_form = ChallengeForm()
    print "Got new form"
    
    challenges = _classroom.challenges
    print "Challenges"
    
    data = {'school':school, 'school_class': _classroom, 'added_challenge':challenge, 'challenge_form':new_form, 'challenges':challenges, 'teams':teams}
    print "Create data var"
    
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
