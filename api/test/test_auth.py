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

    def change_password(self, access_token=None, user_data=None):
        """
        Helper method to change password
        """
        with self.app.app_context():
            if isinstance(access_token, str) and isinstance(user_data, dict):
                response = self.client().post('/auth/reset-password',
                            headers=dict(Authorization="Bearer " +  access_token),
                            data=json.dumps(user_data))
                return response.status_code, json.loads(response.data.decode())
            else:
                raise TypeError('Invalid type of access_token and \
                                user_data for change_password')

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
            access_token = self.get_default_token()
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

    def test_change_password(self):
        """
        A registered user can change their password
        """
        post_data = {
            'old_password': 'password',
            'new_password': 'new password'
        }
        with self.app.app_context():                
            # get access code
            access_token = self.get_default_token()
            # try to change password with wrong access token
            self.unauthorized_request(url='/auth/reset-password', method='POST',
            data=post_data)
            # try to change password with wrong input data
            self.invalid_data_request(url='/auth/reset-password', method='POST',
                invalid_data={'wrong_key':'there should be old_password, new_password'},
                access_token=access_token)
            # change password
            on_password_change = self.change_password(
                                    access_token=access_token, user_data=post_data)
            self.assertEqual(on_password_change[0], 200)
            self.assertEqual(on_password_change[1]['message'], 'Password reset successful')
            # try to login with old password
            on_old_login = self.login_user()
            old_login_response = json.loads(on_old_login.data.decode())
            self.assertEqual(on_old_login.status_code, 401)
            self.assertEqual(old_login_response['message'], 'Invalid username or password. Try again')
            # try to login with new password
            user_data = {
                'username': self.user_data['username'],
                'password': post_data['new_password']
            }
            on_new_login = self.login_user(user_data=user_data)
            new_login_response = json.loads(on_new_login.data.decode())
            self.assertEqual(on_new_login.status_code, 200)
            self.assertTrue(new_login_response['access_token'])
            # try to change password after logging out
            self.make_logged_out_request(url='/auth/reset-password', access_token=access_token,
            method='POST', data={'old_password':post_data['new_password'], 'new_password':'a new pass'})

