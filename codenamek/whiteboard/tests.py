"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import tutor_trove_auth


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_whiteboard_url_is_generated(self):
        """
        Tests that the Tutor Trove authorization url generation does not fail.
        Whether the url is valid or not is another task.
        """
        ttAuth = tutor_trove_auth()
        
        whiteboard_title = "My Title"
        whiteboard_hash = "abcdef"
        user_type = "tutor"
        user_name = "bob"
        user_id = "asdkjlnrtgkjv"
        url = ttAuth.get_whiteboard_url(whiteboard_title, whiteboard_hash, user_type, user_name, user_id)
        self.assertIsNotNone(url, "the url was nothing!")
        print url