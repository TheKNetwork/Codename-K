from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from whiteboard.models import *

class WhiteboardSessionForm(ModelForm):
  class Meta:
      model = WhiteboardSession
      exclude = ('whiteboard_hash','whiteboard_url','date_created','date_modified',)