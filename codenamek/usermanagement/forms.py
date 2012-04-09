from django.db import models
from django.forms import ModelForm
from codenamek.usermanagement.models import UserProfile
 
class ProfileForm(ModelForm):
  class Meta:
      model = UserProfile
      exclude = ('user',)      