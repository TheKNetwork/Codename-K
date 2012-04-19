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