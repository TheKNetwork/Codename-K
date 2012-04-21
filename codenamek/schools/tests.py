from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import *
from codenamek.schools.models import *
from codenamek.schools.schoolmanagement_api import *

from django.test import TestCase

class SimpleTest(TestCase):  
    
    def test_add_school(self):
        school = add_school(school_name="Test School")
        associated_group_name = school.name
        self.assertIsNotNone(associated_group_name, "Saving the school didn't create the correct group entry")
        pass
    
    def test_add_class_to_school(self):
        school = add_school(school_name="Test School")
        
        school_class = add_class(school_id=school.id, _class_name="Math 101")
        associated_group_name = school_class.name
        self.assertIsNotNone(associated_group_name, "Saving the class didn't create the correct group entry")
        pass
    
    def test_add_users_to_team(self):
        bsmith = User.objects.get(username='bsmith')
        cjones = User.objects.get(username='cjones')
        team = create_team_for_tests()
        team_id = team.id
        
        add_user_to_team(bsmith, team)
        add_user_to_team(cjones, team)
        
        team = ClassroomTeam.objects.get(id=team_id)
        self.assertGreater(team.user_set.count(), 0, "No users found for the team!")
        pass
    
    def test_add_challenges_to_team(self):
        team = create_team_for_tests()
        challenge1 = create_challenge_for_team(team, 'Understanding Decimal Place Values')
        challenge2 = create_challenge_for_team(team, 'Understanding Fractions')
        
        print "Team has %s challenges" % team.challenges.count()
        for challenge in team.challenges.all():
            print "Challenge: %s" % challenge
        # self.assertGreater(groups.count(),0,"")
        # self.assertGreater(team.group_challenges.count(),0,"")
        pass
    
    def test_add_team_to_class(self):
        team = create_team_for_tests()
        self.assertIsNotNone(team, "Team is nothing, was there a problem creating it?") 
        pass
    
    def test_get_main_school_for_user(self):
        main_school = get_main_school_for_user(username="pkuperman")
        self.assertIsNotNone(main_school, "There should have been a main school set for the user bsmith, but we can't find one")

