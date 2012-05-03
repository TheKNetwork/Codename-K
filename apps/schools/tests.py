from django.db import models
from django.contrib.auth.models import User, Group
from schools.models import *
from schools.schoolmanagement_api import *
from khanapi.khan_api import *
import simplejson

from django.test import TestCase

class SimpleTest(TestCase):  
    def setUp(self): 
        ccoy_gmail = User.objects.get(username='ccoy')
        ccoy_gmail.get_profile().access_token = 'oauth_token_secret=5zGh7Et8NsWgTsQf&oauth_token=AYGs9kJG394x6X5c'
        ccoy_gmail.save()
        
        self.facebook_token = 'oauth_token_secret=MzMtp5nqUsd5uZaE&oauth_token=T43hUPaKW2nhjYYS'
        self.gmail_token = 'oauth_token_secret=5zGh7Et8NsWgTsQf&oauth_token=AYGs9kJG394x6X5c'
        self.user = ccoy_gmail  
        self.json_string = '[["Number line 2","http://www.khanacademy.org/exercise/number_line_2"],["Adding and subtracting negative numbers","http://www.khanacademy.org/exercise/adding_and_subtracting_negative_numbers"],["Ordering negative numbers","http://www.khanacademy.org/exercise/ordering_negative_numbers"]]'
    
    def test_json_parse(self):
        jsonobj = simplejson.loads(self.json_string)
        for o in jsonobj:
            print o[0]
            print o[1]
            
        pass
        
    
    # GROUP PROFILE MEGA TEST (FOR MENTAL CLARITY)
    def norun_test_group_profile_stuff(self):
        # get reference to a school and a class
        school = add_school(school_name="Rock School")
        school_class = add_class(school_id=school.id, _class_name="Geology 101")
        
        # get or create a user, let's assume this user is an admin
        # TODO: Do we need a flag for that?
        user1 = User(username="user1")
        user2 = User(username="user2")
        
        user1.save()
        user2.save()
        
        # Now that we have profile objects, associate a khan user with each
        # user id. We haven't set these yet, so we'll see warnings and no
        # proficiency will exist.
        user1.get_profile().access_token = self.gmail_token
        user2.get_profile().access_token = self.facebook_token
        
        # Save the updated stuff
        user1.save()
        user2.save()
        
        # Add the users to the groups they should belong to.
        # (technically we could skip to the teams, but let's be accurate here.
        add_user_to_school(user1, school)
        add_user_to_school(user2, school)
        
        add_user_to_class(user1, school_class)
        add_user_to_class(user2, school_class)
        
        #
        #
        # Let's group the class into Teams. Create two teams, put some users in each.
        team1 = add_team_to_class(school_class.id, "The Rockettes")
        team2 = add_team_to_class(school_class.id, "The Slugs")
        
        add_user_to_team(user1, team1)
        add_user_to_team(user2, team2)
        
        # Create a challenge, name it Challenge Set One or something
        challenge_of_decimals = create_challenge_for_class(school_class, "Understanding Decimal Stuff")
        
        add_team_to_challenge(team1, challenge_of_decimals);
        add_team_to_challenge(team2, challenge_of_decimals);
        
        # Pick from a list of Khan exercises
        # Create an empty array to hold some random exercises first
        selected_exercises = []
        
        khan_exercises_json = get_khan_exercises(self.user) # the user here is for auth only
        i = 0
        print "Adding the following 4 random exercises to challenge..."
        print 
        for exercise in khan_exercises_json:
            # print "%s\n---------------------------------\n%s\r\n" % (exercise['name'], exercise['ka_url'])
            if i < 4:
                print "%s\n---------------------------------\n%s\r\n" % (exercise['name'], exercise['ka_url'])
                challenge_exercise = ChallengeExercise(
                                                       exercise_name=exercise['name'], 
                                                       exercise_url=exercise['ka_url'], 
                                                       exercise_description=exercise['description'], 
                                                       challenge=challenge_of_decimals)
                challenge_exercise.save()
                                    
            i = i+1
        
        print "Count of related exercises for our challenge is now %s" % challenge_of_decimals.exercises.count()
        
        team1_pro_date = None
        team2_pro_date = None
        for challenge_ex in challenge_of_decimals.exercises.all():
            is_pro = get_exercise_proficiency_for_team(team1, challenge_ex.exercise_name)
            # Are they proficient?
            print "Is %s pro at %s? %s" % (team1, challenge_ex.exercise_name, is_pro)
            
            # If they ARE proficient, when? (returns the latest date of all dates in collection of user pro dates)
            if is_pro:
                pro_date = get_team_proficiency_date_for_exercise(team, challenge_ex.exercise_name)
            else:
                print "Team 1 is not pro yet!"
                
        # Complete the exercises for the second team, the same way. Check the flags and time
        for challenge_ex in challenge_of_decimals.exercises.all():
            is_pro = get_exercise_proficiency_for_team(team2, challenge_ex.exercise_name)
            # Are they proficient?
            print "Is %s pro at %s? %s" % (team2, challenge_ex.exercise_name, is_pro)
            
            # If they ARE proficient, when? (returns the latest date of all dates in collection of user pro dates)
            if is_pro:
                pro_date = get_team_proficiency_date_for_exercise(team2, challenge_ex.exercise_name)
            else:
                print "Team 2 is not pro yet!"

        pass
    
    # END OF LINE
    
    
    
    def norun_test_add_school(self):
        school = add_school(school_name="Test School")
        associated_group_name = school.name
        self.assertIsNotNone(associated_group_name, "Saving the school didn't create the correct group entry")
        pass
    
    def norun_test_add_challenge(self):
        # get reference to a school and a class
        school = add_school(school_name="Rock School")
        school_class = add_class(school_id=school.id, _class_name="Geology 101")
        
        # get or create a user, let's assume this user is an admin
        # TODO: Do we need a flag for that?
        user1 = User(username="user1")
        user2 = User(username="user2")
        
        user1.save()
        user2.save()
        
        # Now that we have profile objects, associate a khan user with each
        # user id. We haven't set these yet, so we'll see warnings and no
        # proficiency will exist.
        user1.get_profile().access_token = self.gmail_token
        user2.get_profile().access_token = self.facebook_token
        
        # Save the updated stuff
        user1.save()
        user2.save()
        
        # Add the users to the groups they should belong to.
        # (technically we could skip to the teams, but let's be accurate here.
        add_user_to_school(user1, school)
        add_user_to_school(user2, school)
        
        add_user_to_class(user1, school_class)
        add_user_to_class(user2, school_class)
        
        #
        #
        # Let's group the class into Teams. Create two teams, put some users in each.
        team1 = add_team_to_class(school_class.id, "The Rockettes")
        team2 = add_team_to_class(school_class.id, "The Slugs")
        
        add_user_to_team(user1, team1)
        add_user_to_team(user2, team2)
        
        # Create a challenge, name it Challenge Set One or something
        challenge_of_decimals = create_challenge_for_class(school_class, "Understanding Decimal Stuff")
        
        add_team_to_challenge(team1, challenge_of_decimals);
        add_team_to_challenge(team2, challenge_of_decimals);
        
        print "Challenge groups: %s" % challenge_of_decimals.challenge_groups.all().count()
        pass
    
    def norun_test_add_users_to_team(self):
        bsmith = User.objects.get(username='bsmith')
        cjones = User.objects.get(username='cjones')
        team = create_team_for_tests()
        team_id = team.id
        
        add_user_to_team(bsmith, team)
        add_user_to_team(cjones, team)
        
        team = ClassroomTeam.objects.get(id=team_id)
        self.assertGreater(team.user_set.count(), 0, "No users found for the team!")
        pass

    
    def norun_test_add_team_to_class(self):
        team = create_team_for_tests()
        self.assertIsNotNone(team, "Team is nothing, was there a problem creating it?") 
        pass
    
    def norun_test_get_main_school_for_user(self):
        main_school = get_main_school_for_user(username="pkuperman")
        self.assertIsNotNone(main_school, "There should have been a main school set for the user bsmith, but we can't find one")

    def test_count_users_for_school(self):
        school = School.objects.get(school_name="ITT Tech")
        
        users = school.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for ITT Tech. Is it still in the initialdata.json file?")
        pass
        
    def test_count_users_for_class(self):
        school_class = Classroom.objects.get(
            school=(School.objects.get(school_name="ITT Tech"))
            )
        
        users = school_class.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for %s. Is it still in the initialdata.json file?" % school_class.name)
        pass    
    
    def test_get_schools_for_user(self):
        schools = get_schools_for_user(username="pkuperman")
        
        self.assertGreater(schools.count(), 0, "No schools were found but should have been")
        
    def test_invite_a_user_to_math_101(self):
        ccoy = User.objects.get(username="ccoy")
        mustefa = User.objects.get(username="mjoshen")
        school = School.objects.get(school_name="ITT Tech")
        school_class = school.classrooms.filter(class_name="Math 101")[0]
        invitation = invite_user_to_class(ccoy.id, mustefa.id, school_class.id)
        
        count_of_invitations_received = mustefa.invitations_received.count()
        self.assertGreater(count_of_invitations_received, 0, "No invitations were received by mustefa!")
        
        count_of_invitations_sent = ccoy.invitations_sent.count()
        self.assertGreater(count_of_invitations_sent, 0, "No invitations were sent by ccoy!")
        
    def test_accept_class_invitation(self):
        class_invitation = invite_user_to_class_by_lookup_names("ccoy","mjoshen","ITT Tech","Math 101")
        mustefa = User.objects.get(username="mjoshen")
        count_of_invitations_received = mustefa.invitations_received.count()
        self.assertGreater(count_of_invitations_received, 0, "No invitations were received by mustefa")
        
        accept_invitation_to_class(mustefa, class_invitation.id)
        invitations_accepted = mustefa.invitations_received.all()
        count_of_accepted = 0
        for invitation in invitations_accepted:
            if invitation.accepted_on_date != None:
                count_of_accepted = count_of_accepted + 1
        
        
        print "Found %s accepted invitation(s)" % count_of_accepted
        self.assertGreater(count_of_accepted, 0, "No invitations were accepted by mustefa")
        
    def test_reject_class_invitation(self):
        class_invitation = invite_user_to_class_by_lookup_names("ccoy","mjoshen","ITT Tech","Math 101")
        mustefa = User.objects.get(username="mjoshen")
        count_of_invitations_received = mustefa.invitations_received.count()
        self.assertGreater(count_of_invitations_received, 0, "No invitations were received by mustefa")
        
        reject_invitation_to_class(mustefa, class_invitation.id)
        invitations_rejected = mustefa.invitations_received.all()
        count_of_rejected = 0
        for invitation in invitations_rejected:
            if invitation.rejected_on_date != None:
                count_of_rejected = count_of_rejected + 1
        
        
        print "Found %s rejected invitation(s)" % count_of_rejected
        self.assertGreater(count_of_rejected, 0, "No invitations were rejected by mustefa")   
        
    def test_count_invitations_to_class(self):
        ccoy = User.objects.get(username="ccoy")
        mustefa = User.objects.get(username="mjoshen")
        school = School.objects.get(school_name="ITT Tech")
        school_class = school.classrooms.filter(class_name="Math 101")[0]
        invitation = invite_user_to_class(ccoy.id, mustefa.id, school_class.id)
        
        count_of_class_invitations = school_class.invitations.count()
        self.assertGreater(count_of_class_invitations, 0, "No invitations were created for this class")   
