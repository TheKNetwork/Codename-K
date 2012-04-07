from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
     
from django.db.models import signals
from codenamek.usermanagement.signals import *

# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)

def add_user_to_class(class_id, user_id):
    # Get the class from the class id
    # query - 
    
    # Get the user object from the user id
    # user.groups.add(school_class.group)
    # user.save()
    pass

SCHOOL_GENDER_FLAG_CHOICES = (
    ('B','Boys Only'),
    ('G','Girls Only'),
    ('C','Co-ed'),                           
)
    
class UserHistory(models.Model):
    user = models.ForeignKey(User, unique=True)
    event = models.CharField(max_length=255)
    event_time = models.DateTimeField()

class Class(models.Model):
    group = models.ForeignKey(Group, unique=True)
    class_name = models.CharField(max_length=50)
    class_description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')

    def __unicode__(self):
        return u"{0}".format(self.group)

class School(models.Model):
    school_name = models.CharField(max_length=100)
    address_line_one = models.CharField(max_length=100, blank=True)
    address_line_two = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    address_country = models.CharField(max_length=50, blank=True)
    school_url = models.URLField(blank=True)
    gender_flag = models.CharField(max_length=1, choices=SCHOOL_GENDER_FLAG_CHOICES, blank=True)
    classes = models.ManyToManyField(Class, blank=True)
    users = models.ManyToManyField(User, blank=True)
    
    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')

    def __unicode__(self):
        return self.school_name    
    
class UserProfile(models.Model):
    personal_url = models.URLField(blank=True)
    home_address = models.TextField(blank=True)
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def __unicode__(self):
        return self.user.username    