from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import *
from codenamek.schools.models import *
from codenamek.schools.schoolmanagement_api import *

from django.test import TestCase

class SimpleTest(TestCase):  
    
    # GROUP PROFILE MEGA TEST (FOR MENTAL CLARITY)
    def test_group_profile_stuff(self):
        # get reference to a school and a class
        school = add_school(school_name="Rock School")
        school_class = add_class(school_id=school.id, _class_name="Geology 101")
        
        # get or create a user, let's assume this user is an admin
        # TODO: Do we need a flag for that?
        user1 = User(username="user1")
        user2 = User(username="user2")
        user3 = User(username="user3")
        user4 = User(username="user4")
        
        user1.save()
        user2.save()
        user3.save()
        user4.save()
        
        # Now that we have profile objects, associate a khan user with each
        # user id.
        user1.get_profile().access_token = ""
        user2.get_profile().access_token = ""
        user3.get_profile().access_token = ""
        user4.get_profile().access_token = ""
        
        # Save the updated stuff
        user1.save()
        user2.save()
        user3.save()
        user4.save()
        
        # Add the users to the groups they should belong to.
        # (technically we could skip to the teams, but let's be accurate here.
        add_user_to_school(user1, school)
        add_user_to_school(user2, school)
        add_user_to_school(user3, school)
        add_user_to_school(user4, school)
        
        add_user_to_class(user1, school_class)
        add_user_to_class(user2, school_class)
        add_user_to_class(user3, school_class)
        add_user_to_class(user4, school_class)
        
        #
        #
        # Let's group the class into Teams. Create two teams, put some users in each.
        team1 = add_team_to_class(school_class.id, "The Rockettes")
        team2 = add_team_to_class(school_class.id, "The Slugs")
        
        add_user_to_team(user1, team1)
        add_user_to_team(user2, team1)
        
        add_user_to_team(user3, team2)
        add_user_to_team(user4, team2)
        
        # Create a challenge, name it Challenge Set One or something
        challenge_of_decimals = create_challenge_for_teams([team1, team2], "Understanding Decimal Stuff")
        
        # Pick from a list of Khan exercises
        
        
        # put a reference to those (2) exercises in
        #   a child ChallengeExercise record (each)
        
        # Set the knetwork db proficiency to zero
        
        # grab the Khan API proficiency for the exercise, store in record
        
        # Fake-set the proficiency in one team's exercises (each student's proficiency)
        #     to greater than zero, let's just say 1 for now
        
        # check the completed flag and completed time on the challenge
        #     the flag should be set to True, and the time should be not None
        
        # Complete the exercises for the second team, the same way. Check the flags and time
        
        
        pass
    
    # END OF LINE
    
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

    
    def test_add_team_to_class(self):
        team = create_team_for_tests()
        self.assertIsNotNone(team, "Team is nothing, was there a problem creating it?") 
        pass
    
    def test_get_main_school_for_user(self):
        main_school = get_main_school_for_user(username="pkuperman")
        self.assertIsNotNone(main_school, "There should have been a main school set for the user bsmith, but we can't find one")

