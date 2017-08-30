"""
This module is for testing the auth blueprint in app
"""


import unittest
import json
from app import create_app, db
from .common_functions import BaseTestClass


class AuthTestClass(BaseTestClass):
    """
    All tests for the auth blueprint
    """

    def test_registration(self):
        """
        Test that an anonymous user can register successfully
        """
        with self.app.app_context():
            response = self.register_user()
            # convert the json response to an object
            result = json.loads(response.data.decode())
            # the user should be successfully registered
            self.assertEqual(result['message'], 
                            'User registration successful')
            self.assertEqual(response.status_code, 201)
            # sending invalid data, return message error and 400
            self.invalid_data_request(url='/auth/register', method='POST',
            invalid_data={'restriction': 'there should be a name,\
                         password, username and email'}, access_token='')

    def test_cannot_register_twice(self):
        """
        Test that a user cannot be registered twice
        """
        with self.app.app_context():
            result = self.register_user()
            self.assertEqual(result.status_code, 201)
            # register user again
            second_response = self.register_user()
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
            response = self.register_user()
            self.assertEqual(response.status_code, 201)

            # then log in
            response = self.login_user()
            result = json.loads(response.data.decode())
            # You should have a success message
            self.assertEqual(result['message'], 'Login successful')
            # the status code should also be 200
            self.assertEqual(response.status_code, 200)
            # a token should also be present
            self.assertTrue(result['access_token'])
            # sending invalid data, return message error and 400
            self.invalid_data_request(url='/auth/login', method='POST',
            invalid_data={'restriction': 'there should be a \
                         password and username'}, access_token='')

    def test_non_registered_user_login(self):
        """
        A non registered user should not be logged in
        """
        with self.app.app_context():
            # login without registering first
            response = self.login_user()
            result = json.loads(response.data.decode())
            # You should have a success message
            self.assertEqual(result['message'], 'Invalid username or password. Try again')
            # the status code should also be 401
            self.assertEqual(response.status_code, 401)
            # a token should also be absent
            self.assertNotIn('access_token', result.keys())

    def test_logout(self):
        """
        A registered user should be able to logout
        """
        with self.app.app_context():
            # register the user
            on_registration = self.register_user()
            self.assertEqual(on_registration.status_code, 201)
            # login and see user logs in
            on_login = self.login_user()
            self.assertEqual(on_login.status_code, 200)
            login_response = json.loads(on_login.data.decode())
            access_token = login_response['access_token']
            # attempt to logout
            on_logout = self.logout_user(access_token=access_token)
            self.assertEqual(on_logout.status_code, 200)
            logout_response = json.loads(on_logout.data.decode())
            self.assertEqual(logout_response['message'], 'Logout successful')
            # attempt to logout again
            on_logout_again = self.logout_user(access_token=access_token)
            self.assertEqual(on_logout_again.status_code, 401)
            logout_response = json.loads(on_logout_again.data.decode())
            self.assertEqual(logout_response['message'], 'You are already logged out')
            # attempt to logout with a crappy token
            on_invalid_token_logout = self.logout_user(access_token="invalid token")
            self.assertEqual(on_invalid_token_logout.status_code, 401)
            logout_response = json.loads(on_invalid_token_logout.data.decode())
            self.assertEqual(logout_response['message'], 
                'Token is invalid. Try to login.')

# there is need for changing password tests
