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
            response = self.client().post('auth/register', 
                             data=json.dumps(self.user_data))
            # convert the json response to an object
            result = json.loads(response.data.decode())
            # the user should be successfully registered
            self.assertEqual(result['message'], 
                            'User registration successful')
            self.assertEqual(response.status_code, 201)

            # sending invalid data, return message error and 400

    def test_cannot_register_twice(self):
        """
        Test that a user cannot be registered twice
        """
        with self.app.app_context():
            result = self.client().post('/auth/register',
                                 data=json.dumps(self.user_data))
            self.assertEqual(result.status_code, 201)
            # register user again
            second_response = self.client().post('/auth/register',
                                         data=json.dumps(self.user_data))
            self.assertEqual(second_response.status_code, 202)
            # get the results returned in json format
            result = json.loads(second_response.data.decode())
            self.assertEqual(
                result['message'], "User already exists. Please login")

    def test_user_login(self):
        """
        Test if a user can log in
        """
        with self.app.app_context():
            # first register the user
            response = self.client().post('/auth/register',
                                 data=json.dumps(self.user_data))
            self.assertEqual(response.status_code, 201)

            # then log in
            login_details = dict(username=self.user_data['username'],
                                password=self.user_data['password'])
            response = self.client().post('/auth/login', 
                                    data=json.dumps(login_details))
            result = json.loads(response.data.decode())
            # You should have a success message
            self.assertEqual(result['message'], 'Login successful')
            # the status code should also be 200
            self.assertEqual(response.status_code, 200)
            # a token should also be present
            self.assertTrue(result['access_token'])

            # sending invalid data, return message error and 400

    def test_non_registered_user_login(self):
        """
        A non registered user should not be logged in
        """
        with self.app.app_context():
            # login without registering first
            login_details = dict(username=self.user_data['username'],
                                password=self.user_data['password'])
            response = self.client().post('/auth/login', 
                                    data=json.dumps(login_details))
            result = json.loads(response.data.decode())
            # You should have a success message
            self.assertEqual(result['message'], 'Invalid username or password. Try again')
            # the status code should also be 401
            self.assertEqual(response.status_code, 401)
            # a token should also be absent
            self.assertNotIn('access_token', result.keys())

# there is need for a blacklist models
# there is need for logout tests
