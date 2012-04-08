from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import *

from django.test import TestCase

class SimpleTest(TestCase):
    def test_add_school(self):
        school = add_school(school_name="Test School")
        associated_group_name = school.name
        self.assertIsNotNone(associated_group_name, "Saving the school didn't create the correct group entry")
        print "Auto-created (school) group name is %s" % associated_group_name
        pass
    
    def test_add_class_to_school(self):
        school = add_school(school_name="Test School")
        
        school_class = add_class(school_id=school.id, class_name="Math 101")
        associated_group_name = school_class.name
        self.assertIsNotNone(associated_group_name, "Saving the class didn't create the correct group entry")
        print "Auto-created (class) group name is %s" % associated_group_name
        pass
    
    def test_count_users_for_school(self):
        school = School.objects.get(school_name="ITT Tech")
        print "School retrieved is %s" % school.name
        
        users = school.user_set.all()
        count_of = users.count()
        
        self.assertGreater(count_of, 0, "No users found for ITT Tech. Is it still in the initialdata.json file?")
        
        print "Count of users for school is %s" % count_of
        pass
        
    
