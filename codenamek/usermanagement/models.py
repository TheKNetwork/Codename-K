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
    """
    When a user does stuff, we want to track some of it. As yet
    mostly undefined.
    """
    user = models.ForeignKey(User, unique=True)
    event = models.CharField(max_length=255)
    event_time = models.DateTimeField()

class School(Group):
    """
    The school object represents, as you could probably guess, a school. A school
    IS a django group, which makes it easy to manage authorization and membership
    without getting too complex.
    """
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
    """
    A class is an organization within a school. It might physically be many things,
    but it amounts to a grouping of people that attend a class, usually. A class might
    even end up being a study group. As is the case with a school object, the Class
    that belongs to a school is also a django auth group for the same reasons as the
    school object.
    """
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
    """
    A class invitation is a record that is marked as accepted or rejected, bound
    to the inviting user and the user that is invited, along with the class they
    have been invited to.
    """
    school_class = models.ForeignKey(Class, related_name="invitations")
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
    """
    A user profile contains extra information about a user beyond that of the
    existing django auth User object.
    """
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