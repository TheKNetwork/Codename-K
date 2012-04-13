from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import Group
from django import forms

from codenamek.usermanagement.models import Class
 
 
class SchoolClassForm(ModelForm):
  class Meta:
      model = Class
      exclude = ('group',)