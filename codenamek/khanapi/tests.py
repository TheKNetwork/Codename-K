from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import *
from codenamek.khanapi.khan_api import *

from django.test import TestCase

class SimpleTest(TestCase):
        
    def setUp(self): 
        ccoy = User.objects.get(username='ccoy')
        ccoy.get_profile().access_token = 'oauth_token_secret=5zGh7Et8NsWgTsQf&oauth_token=AYGs9kJG394x6X5c'
        ccoy.save()
        self.user = ccoy     
        
    def test_get_khan_user_data(self):
        jsondata = get_khan_user(self.user)
        self.assertIsNotNone(jsondata)
        
    def test_get_exercises(self):
        jsondata = get_khan_exercises(self.user)
        self.assertIsNotNone(jsondata)
            
    def test_get_exercise_history(self):
        jsondata = get_khan_exercise_history(self.user)
        self.assertIsNotNone(jsondata)
            
    def test_get_profiency_for_exercise(self):
        exercise_states = get_proficiency_for_exercise(self.user, 'scientific_notation')
        print "Proficient? %s" % exercise_states['proficient']
        print "Struggling? %s" % exercise_states['struggling']
        print "Reviewing ? %s" % exercise_states['reviewing']