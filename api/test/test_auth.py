"""
This module is for testing the auth blueprint in app
"""


import unittest
import json
from app import create_app, db


class AuthTestClass(unittest.TestCase):
    """
    All tests for the auth blueprint
    """

    def setUp(self):
        """
        initialize the app, db and some variables
        """
        self.app = create_app(config_name='testing')
        # a client to test the endpoints of the auth blueprint
        self.client = self.app.test_client
        # sample user data
        self.user_data = {
            'username': 'johndoe',
            'password': 'password',
            'name': 'john doe',
            'email': 'johndoe@example.com'
        }

        with self.app.app_context():
            # create tables in test db
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """
        Test that an anonymous user can register successfully
        """
        with self.app.app_context():
            response = self.client().post('auth/register', data=json.dumps(self.user_data))
            # convert the json response to an object
            result = json.loads(response.data.decode())
            # the user should be successfully registered
            self.assertEqual(result['message'], 'User registration successful')
            self.assertEqual(response.status_code, 201)

    def test_cannot_register_twice(self):
        """
        Test that a user cannot be registered twice
        """
        with self.app.app_context():
            result = self.client().post('/auth/register', data=json.dumps(self.user_data))
            self.assertEqual(result.status_code, 201)
            # register user again
            second_response = self.client().post('/auth/register', data=json.dumps(self.user_data))
            self.assertEqual(second_response.status_code, 202)
            # get the results returned in json format
            result = json.loads(second_response.data.decode())
            self.assertEqual(
                result['message'], "User already exists. Please login")