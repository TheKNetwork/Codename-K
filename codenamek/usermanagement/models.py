from django.db import models
from django.contrib.auth.models import User
     
from django.db.models import signals
from codenamek.usermanagement.signals import create_profile
 
# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)     
     
class UserProfile(models.Model):
    personal_url = models.URLField()
    home_address = models.TextField()
    user = models.ForeignKey(User, unique=True)