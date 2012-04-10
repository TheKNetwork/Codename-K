from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import *

from django.test import TestCase

class SimpleTest(TestCase):
    def test_add_school(self):
        school = add_school(school_name="Test School")
        associated_group_name = school.name
        self.assertIsNotNone(associated_group_name, "Saving the school didn't create the correct group entry")
        pass
    
    def test_add_class_to_school(self):
        school = add_school(school_name="Test School")
        
        school_class = add_class(school_id=school.id, class_name="Math 101")
        associated_group_name = school_class.name
        self.assertIsNotNone(associated_group_name, "Saving the class didn't create the correct group entry")
        pass
    
    def test_count_users_for_school(self):
        school = School.objects.get(school_name="ITT Tech")
        
        users = school.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for ITT Tech. Is it still in the initialdata.json file?")
        pass
        
    def test_count_users_for_class(self):
        school_class = Class.objects.get(
            school=(School.objects.get(school_name="ITT Tech"))
            )
        
        users = school_class.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for %s. Is it still in the initialdata.json file?" % school_class.name)
        pass    
    
    def test_get_schools_for_user(self):
        schools = get_schools_for_user(username="bsmith")
        
        self.assertGreater(schools.count(), 0, "No schools were found but should have been")
        
    def test_get_main_school_for_user(self):
        main_school = get_main_school_for_user(username="bsmith")
        self.assertIsNotNone(main_school, "There should have been a main school set for the user bsmith, but we can't find one")
        
    def test_invite_a_user_to_math_101(self):
        ccoy = User.objects.get(username="ccoy")
        mustefa = User.objects.get(username="mjoshen")
        school = School.objects.get(school_name="ITT Tech")
        school_class = school.class_set.filter(class_name="Math 101")[0]
        invite_user_to_class(ccoy.id, mustefa.id, school_class.id)
        
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
        