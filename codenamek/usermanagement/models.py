"""
This file is responsible for the db set up and relationships of user management.
The actual methods used to manipulate these objects should be placed in
usermanagement_api.py.
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist
import os, datetime

from codenamek.usermanagement.signals import *
from codenamek.schools.models import *

# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)

class UserProfile(models.Model):
    """
    A user profile contains extra information about a user beyond that of the
    existing django auth User object.
    """
    personal_url = models.URLField(blank=True)
    home_address = models.TextField(blank=True)
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def __unicode__(self):
        return self.user.username 
    
class UserHistory(models.Model):
    """
    When a user does stuff, we want to track some of it. As yet
    mostly undefined.
    """
    user = models.ForeignKey(User, unique=True)
    event = models.CharField(max_length=255)
    event_time = models.DateTimeField()