from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import *
from codenamek.khanapi.khan_api import *
import simplejson

from django.test import TestCase

class SimpleTest(TestCase):
        
    def setUp(self): 
        ccoy = User.objects.get(username='ccoy')
        ccoy.get_profile().access_token = 'oauth_token_secret=5zGh7Et8NsWgTsQf&oauth_token=AYGs9kJG394x6X5c'
        ccoy.save()
        self.user = ccoy    
        
                 
    def test_get_playlist_library(self):
        jsondata = get_khan_playlist_library(self.user)
        # print jsondata
        for topic in jsondata:
            print "Topic name: %s" % topic['name']
            if topic.has_key('items'):
                for subtopic in topic['items']:
                    if subtopic.has_key('name'):
                        print "    Subtopic name: %s" % subtopic['name']
                        if subtopic.has_key('items'):
                            for subtopic_item in subtopic['items']:
                                print "         Subtopic item: %s" % subtopic_item['name']
                                if subtopic_item.has_key('items'):
                                    for subtopic_item_key in subtopic_item['items']:
                                        print "             SubSubTopic key:%s" % subtopic_item_key
                                        print "             SubSubTopic item:%s" % subtopic_item['items']
                    
        self.assertIsNotNone(jsondata)
        
    def test_get_khan_user_data(self):
        csantiago = User.objects.get(username="csantiago")
        jsondata = get_khan_user(csantiago)
        print jsondata
        self.assertIsNotNone(jsondata)
       
    def test_get_khan_badges(self):
        jsondata = get_khan_badges(self.user)
        self.assertIsNotNone(jsondata)
         
    def test_get_exercises(self):
        csantiago = User.objects.get(username="csantiago")
        jsondata = get_khan_exercises(csantiago)
        self.assertIsNotNone(jsondata)
            
    def test_get_exercise_history(self):
        jsondata = get_khan_exercise_history(self.user)
        self.assertIsNotNone(jsondata)

          
    def test_get_profiency_for_exercise(self):
        csantiago = User.objects.get(username="csantiago")
        exercise_pro = get_proficiency_for_exercise(csantiago, 'Addition 1')
        print "Proficient? %s" % exercise_pro