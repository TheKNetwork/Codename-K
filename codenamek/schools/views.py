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

@login_required
def index(request):
    schools = get_schools_for_user(id=request.user.id)
    data = {'user': request.user, 'schools': schools}
    return render(request, "schools/schools.html", data)

@login_required
def classes_for_school(request, school_id):
    school = School.objects.get(id=school_id)
    classes = school.class_set.all()
    data = {'user': request.user, 'school':school, 'classes': classes}
    return render(request, "schools/classes.html", data)

@login_required
def class_congregation(request, school_id, class_id):
    school_class = Class.objects.get(id=class_id)
    school = School.objects.get(id=school_id)
    data = {'user': request.user, 'school_class': school_class, 'school':school}
    return render(request, "schools/class_congregation.html", data)
