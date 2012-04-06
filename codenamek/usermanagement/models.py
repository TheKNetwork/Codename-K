from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
     
from django.db.models import signals
from codenamek.usermanagement.signals import *
 
# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)
signals.post_save.connect(create_class, sender=Group)

SCHOOL_GENDER_FLAG_CHOICES = (
    ('B','Boys Only'),
    ('G','Girls Only'),
    ('C','Co-ed'),                           
)


class UserProfile(models.Model):
    personal_url = models.URLField()
    home_address = models.TextField()
    is_teacher = models.BooleanField()
    is_student = models.BooleanField()
    user = models.ForeignKey(User, unique=True)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def __unicode__(self):
        return self.user.username


class Class(models.Model):
    class_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, unique=True)

    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')

    def __unicode__(self):
        return u"{0} - {1}".format(self.class_name, self.group)


class School(models.Model):
    school_name = models.CharField(max_length=100)
    address_line_one = models.CharField(max_length=100)
    address_line_two = models.CharField(max_length=100)
    address_city = models.CharField(max_length=100)
    address_state = models.CharField(max_length=2)
    address_country = models.CharField(max_length=50)
    school_url = models.URLField()
    gender_flag = models.CharField(max_length=1, choices=SCHOOL_GENDER_FLAG_CHOICES)
    classes = models.ManyToManyField(Class)

    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')

    def __unicode__(self):
        return self.school_name
    