from django.db import models
from django.contrib.auth.models import User, Group
from schools.models import *
from schools.schoolmanagement_api import *
from schools.usermanagement_api import *
from khanapi.khan_api import *
import simplejson

from django.test import TestCase

class SimpleTest(TestCase):
    
    def norun_test_json_parse(self):
        jsonobj = simplejson.loads(self.json_string)
        for o in jsonobj:
            print o[0]
            print o[1]
            
        pass

    # END OF LINE
    
    def xtest_show_challenges_for_user(self):
        user = User.objects.get(username='csantiago')
        map_unfinished_stuff, found_any = get_unfinished_challenges_for_user(user_id=user.id)
        print "Found any? %s" % found_any
        
        for team in map_unfinished_stuff:
            print "Team name: %s" % team
            unfinished_challenges = map_unfinished_stuff[team]
            for uc in unfinished_challenges:
                print "    Challenge: %s" % uc
                for ue in unfinished_challenges[uc]:
                    print "        Exercise: %s" % ue
    
    def norun_test_add_school(self):
        school = add_school(school_name="Test School")
        associated_group_name = school.name
        self.assertIsNotNone(associated_group_name, "Saving the school didn't create the correct group entry")
        pass
    
    def test_info_for_team_view(self):
        team = ClassroomTeam.objects.get(team_name="UE")
        print "Team: %s" % team
        
        for user in team.user_set.all():
            print "  Member: %s: %s, %s" % (user, user.last_name, user.first_name)
        
        print "Challenges: completed %s out of %s challenges" % (team.challenge_complete_count, team.challenges.count())
        
        for challenge in team.challenges.all():
            print "  %s" % challenge
        
            complete_count = 0
            for exercise in challenge.exercises.all():
                ex_pro = get_exercise_proficiency_for_team(team, exercise.exercise_name)
                print "Exercise %s complete? %s" % (exercise, ex_pro)
                if ex_pro:
                    complete_count = complete_count + 1
        
            print "Challenge exercise complete count: %s" % complete_count
        
        user_ex = []
        for user in team.user_set.all():
            ex_status = {}
            for exercise in challenge.exercises.all():
                ex_status['user'] = user
                ex_status['exercise'] = exercise
                user_ex_pro = get_proficiency_for_exercise(user, exercise.exercise_name)
                ex_status['is_pro'] = user_ex_pro
            user_ex.append(ex_status)
    
        for item in user_ex:
            # print item
            print "%s - %s: %s" % (item['user'], item['exercise'],item['is_pro'])
    
    def xtest_get_teams_for_challenge(self):
        teams = get_team_status_for_challenge(challenge_id=1)
        for team in teams:
            print team['team']
            for exercise in team['exercises']:
                print '  exercise: %s, team is pro/complete? %s' % (exercise['exercise'], exercise['is_pro'])
                for user in exercise['users']:
                    print '        user:%s is pro/complete? %s' % (user['user'], user['is_pro'])
    
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

    def norun_test_count_users_for_school(self):
        school = School.objects.get(school_name="ITT Tech")
        
        users = school.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for ITT Tech. Is it still in the initialdata.json file?")
        pass
        
    def norun_test_count_users_for_class(self):
        school_class = Classroom.objects.get(
            school=(School.objects.get(school_name="ITT Tech"))
            )
        
        users = school_class.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for %s. Is it still in the initialdata.json file?" % school_class.name)
        pass    
    
    def norun_test_get_schools_for_user(self):
        schools = get_schools_for_user(username="pkuperman")
        
        self.assertGreater(schools.count(), 0, "No schools were found but should have been")
        
    def norun_test_invite_a_user_to_math_101(self):
        ccoy = User.objects.get(username="ccoy")
        mustefa = User.objects.get(username="mjoshen")
        school = School.objects.get(school_name="ITT Tech")
        school_class = school.classrooms.filter(class_name="Math 101")[0]
        invitation = invite_user_to_class(ccoy.id, mustefa.id, school_class.id)
        
        count_of_invitations_received = mustefa.invitations_received.count()
        self.assertGreater(count_of_invitations_received, 0, "No invitations were received by mustefa!")
        
        count_of_invitations_sent = ccoy.invitations_sent.count()
        self.assertGreater(count_of_invitations_sent, 0, "No invitations were sent by ccoy!")
        
    def norun_test_accept_class_invitation(self):
        class_invitation = invite_user_to_class_by_lookup_names("ccoy", "mjoshen", "ITT Tech", "Math 101")
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
        
    def norun_test_reject_class_invitation(self):
        class_invitation = invite_user_to_class_by_lookup_names("ccoy", "mjoshen", "ITT Tech", "Math 101")
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
        
    def norun_test_count_invitations_to_class(self):
        ccoy = User.objects.get(username="ccoy")
        mustefa = User.objects.get(username="mjoshen")
        school = School.objects.get(school_name="ITT Tech")
        school_class = school.classrooms.filter(class_name="Math 101")[0]
        invitation = invite_user_to_class(ccoy.id, mustefa.id, school_class.id)
        
        count_of_class_invitations = school_class.invitations.count()
        self.assertGreater(count_of_class_invitations, 0, "No invitations were created for this class")   
