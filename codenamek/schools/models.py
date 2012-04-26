"""
This file is responsible for the db set up and relationships of school and class management.
The actual methods used to manipulate these objects should be placed in
schoolmanagement_api.py.
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist

from codenamek.usermanagement.models import *

import os, datetime

SCHOOL_GENDER_FLAG_CHOICES = (
    ('B','Boys Only'),
    ('G','Girls Only'),
    ('C','Co-ed'),                           
)

class School(Group):
    """
    The school object represents, as you could probably guess, a school. A school
    IS a django group, which makes it easy to manage authorization and membership
    without getting too complex.
    """
    school_name = models.CharField(max_length=255, unique=True)
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

class Classroom(Group):
    """
    A classroom is an organization within a school. It might physically be many things,
    but it amounts to a grouping of people that attend a class, usually. A classroom might
    even end up being a study group. As is the case with a school object, the Classroom
    that belongs to a school is also a django auth group for the same reasons as the
    school object.
    """
    class_name = models.CharField(max_length=50)
    class_description = models.TextField(blank=True)
    school = models.ForeignKey(School, related_name="classrooms")

    objects = models.Manager()

    class Meta:
        verbose_name = _('Classroom')
        verbose_name_plural = _('Classrooms')

    def __unicode__(self):
        return u"{0}".format(self.class_name)    
    
class Challenge(models.Model):
    challenge_name = models.CharField(max_length=50)
    classroom = models.ForeignKey(Classroom, null=True, blank=True, related_name="challenges")
    
    objects = models.Manager()

    class Meta:
            verbose_name = _('Challenge')
            verbose_name_plural = _('Challenges')

    def __unicode__(self):
        return u"{0}".format(self.challenge_name) 
       
class ClassroomTeam(Group):
    """
    A team is a 'temporary' grouping of people who compete within a class
    or just want to track progress together.
    """
    classroom = models.ForeignKey(Classroom, related_name="teams")
    team_name = models.CharField(max_length=50)

    challenges = models.ManyToManyField(Challenge, through='GroupChallenge')
    
    objects = models.Manager()

    class Meta:
            verbose_name = _('Classroom Team')
            verbose_name_plural = _('Classroom Teams')

    def __unicode__(self):
        return u"{0}".format(self.team_name) 
    
challenge_SCOPE_CHOICES = (
    ('S','School'),
    ('C','Class'),
    ('T','Team'),                           
)
    
class GroupChallenge(models.Model):
    classroom_team = models.ForeignKey(ClassroomTeam)
    challenge = models.ForeignKey(Challenge, related_name="challenge_groups")
    
class ChallengeExercise(models.Model):
    challenge = models.ForeignKey(Challenge, related_name="exercises")
    exercise_name = models.CharField(max_length=150)
    exercise_url = models.URLField(blank=True)
    exercise_description = models.CharField(max_length=2000, null=True, blank=True)
    
class ClassInvitation(models.Model):
    """
    A class invitation is a record that is marked as accepted or rejected, bound
    to the inviting user and the user that is invited, along with the class they
    have been invited to.
    """
    school_class = models.ForeignKey(Classroom, related_name="invitations")
    invited_user = models.ForeignKey(User, related_name="invitations_received")
    invited_by = models.ForeignKey(User, related_name="invitations_sent")
    invited_on_date = models.DateTimeField(auto_now_add=True)
    rejected_on_date = models.DateTimeField(null=True, blank=True)
    accepted_on_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Classroom invitation')
        verbose_name_plural = _('Classroom invitations')

    def __unicode__(self):
        return "Invitation to classroom:(%s) sent to %s from %s" % (self.school_class, self.invited_user, self.invited_by)