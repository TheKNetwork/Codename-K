from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import Group
from django import forms

from codenamek.usermanagement.models import *
from codenamek.schools.models import *
 
class ClassroomForm(ModelForm):
  class Meta:
      model = Classroom
      exclude = ('name','permissions','class_description','school')
      
class ClassroomTeamForm(ModelForm):
    class Meta:
        model = ClassroomTeam
        exclude = ('classroom','challenges','name','permissions')      