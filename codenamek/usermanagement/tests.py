from django.db import models
from django.contrib.auth.models import User, Group
from codenamek.usermanagement.models import School, Class

from django.test import TestCase

class SimpleTest(TestCase):
    def test_add_a_user(self):
        """
        1. Creates a user record
        2. Creates a school
        3. Creates a class belonging to the school
        4. Makes the user a member of the school
        5. Makes the user a member of the class
        """
        # Create a basic user record
        user = User.objects.create_user("TestUser", "testuser@email.com", "password")
        user.save()
        
        print "User id: %s" % user.id
        print "User name: %s" % user
        self.assertIsNotNone(user.id, "Whoops. The user was not saved!")
    
        #
        # Create a school
        test_school = School.objects.create(school_name="Test School")
        test_school.save()
        print "School id: %s" % test_school.id
        self.assertIsNotNone(test_school.id, "Egads. The school was not saved!")
        
        #
        # Create a group (this is strictly a backend process)
        test_group = Group.objects.create(name="Test school - Math 101")
        test_group.save()
        self.assertIsNotNone(test_group.id, "Crikey. The group was not saved!")
        
        #
        # Create a class and bind the class to an auth Group object
        school_class = Class.objects.create(class_name="Math 101", group=test_group)
        school_class.save()
        
        #
        # Add the class to the school's class collection
        test_school.classes.add(school_class)
        test_school.save()
        
        self.assertEqual(1, test_school.classes.count(), "Class count was not 1!")
        
        #
        # Add the user to the class' underlying group object
        user.groups.add(school_class.group)
        user.save()
        
        #
        # Add the school to the user's schools collection
        test_school.users.add(user)
        test_school.save()
        
        pass
