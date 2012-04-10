from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist
import os, datetime

from codenamek.usermanagement.signals import *

# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)

def add_school(**kwargs):
    school = School.objects.create(**kwargs)
    school.name = 'school.%s' % school.school_name
    school.save()
    return school

def add_class(school_id, **kwargs):
    existing_school = School.objects.get(id=school_id)
    school_class = Class.objects.create(school=existing_school, **kwargs)
    school_class.name = 'class.%s.%s' % (existing_school.school_name, school_class.class_name)
    school_class.save()
    return school_class

def get_schools_for_user(**kwargs):
    user = User.objects.get(**kwargs)
    schools = School.objects.filter(group_ptr=user.groups.filter(name__startswith="school."))
    return schools

def get_main_school_for_user(**kwargs):
    user = User.objects.get(**kwargs)
    user_profile = UserProfile.objects.get(user__id=user.id)
    return user_profile.main_school

def invite_user_to_class(inviting_user_id, invited_user_id, school_class_id):
    invited_by = User.objects.get(id=inviting_user_id)
    invited_user = User.objects.get(id=invited_user_id)
    school_class = Class.objects.get(id=school_class_id)
    class_invitation = ClassInvitation.objects.create(
                            school_class=school_class,
                            invited_user=invited_user,
                            invited_by=invited_by
                        )
    return class_invitation
    
def invite_user_to_class_by_lookup_names(inviting_user_name, invited_user_name, school_name, school_class_name):
    print "inviting user name %s" % inviting_user_name
    print "invited user name %s" % invited_user_name
    ccoy = User.objects.get(username=inviting_user_name)
    mustefa = User.objects.get(username=invited_user_name)
    school = School.objects.get(school_name=school_name)
    school_class = school.class_set.filter(class_name=school_class_name)[0]
    return invite_user_to_class(ccoy.id, mustefa.id, school_class.id)
    
def accept_invitation_to_class(current_user, invitation_id):
    existing_invitations = current_user.invitations_received.filter(id=invitation_id)
    for invitation in existing_invitations:
        if invitation.id == invitation_id:
            invitation.accepted_on_date = datetime.datetime.now()
            invitation.save()
            return invitation
        
    raise "No matching invitation found."

def reject_invitation_to_class(current_user, invitation_id):
    existing_invitations = current_user.invitations_received.filter(id=invitation_id)
    for invitation in existing_invitations:
        if invitation.id == invitation_id:
            invitation.rejected_on_date = datetime.datetime.now()
            invitation.save()
            return invitation
        
    raise "No matching invitation found."

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