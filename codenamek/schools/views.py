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

@login_required
def index(request):
    schools = get_schools_for_user(id=request.user.id)
    data = {'user': request.user, 'schools': schools}
    return render(request, "schools/schools.html", data)

@login_required
def create_a_class(request, _school_id):
    if request.method == 'POST': # If the form has been submitted...
        form = ClassroomForm(request.POST)
        if form.is_valid(): 
            classroom = add_class(school_id=_school_id, 
                      class_name=form.cleaned_data['class_name'], 
                      class_description=form.cleaned_data['class_name'] )
            
            add_user_to_class(request.user, classroom)
            print "Added %s" % (form.cleaned_data['class_name'])
            return HttpResponseRedirect('/homeroom/') 
    else:
        form = ClassroomForm() # An unbound form

    return render_to_response('schools/add_class.html', {
        'form': form, 'school_id': _school_id,
    }, context_instance=RequestContext(request, {}))

@login_required
def classes_for_school(request, school_id):
    school = School.objects.get(id=school_id)
    classes = school.classrooms.all()
    data = {'user': request.user, 'school':school, 'classes': classes}
    return render(request, "schools/classes.html", data)

@login_required
def class_congregation(request, school_id, class_id):
    school_class = Classroom.objects.get(id=class_id)
    school = School.objects.get(id=school_id)
    chat_url = '/chat'
    data = {'user': request.user, 'school_class': school_class, 'school':school, 'chat_url': chat_url}
    return render(request, "schools/class_congregation.html", data)
