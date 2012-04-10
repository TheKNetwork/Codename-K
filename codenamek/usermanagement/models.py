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

# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)

SCHOOL_GENDER_FLAG_CHOICES = (
    ('B','Boys Only'),
    ('G','Girls Only'),
    ('C','Co-ed'),                           
)
    
class UserHistory(models.Model):
    user = models.ForeignKey(User, unique=True)
    event = models.CharField(max_length=255)
    event_time = models.DateTimeField()

class School(Group):
    school_name = models.CharField(max_length=100, unique=True)
    address_line_one = models.CharField(max_length=100, blank=True)
    address_line_two = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    address_country = models.CharField(max_length=50, blank=True)
    school_url = models.URLField(blank=True)
    gender_flag = models.CharField(max_length=1, choices=SCHOOL_GENDER_FLAG_CHOICES, blank=True)
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')

    def __unicode__(self):
        return self.school_name    
    

class Class(Group):
    class_name = models.CharField(max_length=50)
    class_description = models.TextField(blank=True)
    school = models.ForeignKey(School)

    objects = models.Manager()

    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')

    def __unicode__(self):
        return u"{0}".format(self.class_name)    
    
class ClassInvitation(models.Model):
    school_class = models.ForeignKey(Class)
    invited_user = models.ForeignKey(User, related_name="invitations_received")
    invited_by = models.ForeignKey(User, related_name="invitations_sent")
    invited_on_date = models.DateTimeField(auto_now_add=True)
    rejected_on_date = models.DateTimeField(null=True, blank=True)
    accepted_on_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Class invitation')
        verbose_name_plural = _('Class invitations')

    def __unicode__(self):
        return "Invitation to class:(%s) sent to %s from %s" % (self.school_class, self.invited_user, self.invited_by)
    
class UserProfile(models.Model):
    personal_url = models.URLField(blank=True)
    home_address = models.TextField(blank=True)
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    main_school = models.ForeignKey(School, null=True, blank=True)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def __unicode__(self):
        return self.user.username    