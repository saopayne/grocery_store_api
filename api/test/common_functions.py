"""
This file holds all the functions common in the tests files
"""
import unittest
import json
from app.models.shopping import User, ShoppingList, ShoppingItem
from app import create_app, db

class ShoppingParentTestClass(unittest.TestCase):
    """
    The test class to be inherited from by tests for
    ShoppingList and ShoppingItem
    """
    def setUp(self):
        """
        Set up the db, the app and some variables
        """
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist_data = {'title': 'Groceries and Home stuff'}
        self.shoppingitem_data = {'name':'fruit', 'quantity':5, 'unit': 'units'}

        with self.app.app_context():
            db.create_all()

    def register_user(self, username="rondoe", email="rondoe@email.com",
                    password="password", name="Ron Doe"):
        """
        Helper function to register user
        """
        with self.app.app_context():
            user_data = {
                'username': username,
                'email': email,
                'password': password,
                'name': name
            }
            return self.client().post('/auth/register', 
                            data=json.dumps(user_data))

    def login_user(self, username="rondoe", password="password"):
        """
        Helper function to log in user
        """
        with self.app.app_context():
            user_data = {
                'username': username,
                'password': password
            }
            return self.client().post('/auth/login', 
                    data=json.dumps(user_data))

    def make_request(self, method, *args, **kwargs):
        """
        Helper method to make requests based on the method arg
        """
        with self.app.app_context():
            if method == 'POST':
                return self.client().post(*args, **kwargs)
            elif method == 'GET':
                return self.client().get(*args, **kwargs)
            elif method == 'PUT':
                return self.client().put(*args, **kwargs)
            elif method == 'DELETE':
                return self.client().delete(*args, **kwargs)
            else:
                raise ValueError('Arguments are invalid for make request')

    def invalid_data_request(self, url=None, 
        method='POST', invalid_data=None, access_token=None):
        """
        Helper method to test invalid data for POST and PUT
        """
        allowed_methods = ('PUT', 'POST')
        invalid_data_message = 'The data you sent was in the wrong structure'
        with self.app.app_context():
            if method in allowed_methods and (isinstance(invalid_data, dict)
             or not invalid_data) and isinstance(url, str) and isinstance(access_token, str):
                # sending invalid data, return message error and 400
                on_attempt = self.make_request(method, url,
                            headers=dict(Authorization='Bearer ' + access_token),
                            data=json.dumps(invalid_data)
                            )
                self.assertEqual(on_attempt.status_code, 400)
                attempt_response = json.loads(on_attempt.data.decode())
                self.assertEqual(attempt_response['message'],
                                invalid_data_message)
            else:
                # after all the elif's if nothing matches, raise an error
                raise ValueError('The arguments are invalid for invalid data request')

    def unauthorized_request(self, url=None, method='POST', data=None):
        """
        Helper method to test for unauthorized/unauthenticated requests
        for POST, PUT, GET, DELETE
        """
        post_or_put = ('POST', 'PUT')
        get_or_delete = ('GET', 'DELETE')
        unauthorized_access_message = 'You do not have the appropriate permissions'
        if method in post_or_put and isinstance(data, dict) and isinstance(url, str):
            with self.app.app_context():
                # sending data without appropriate auth, return message error and 403
                on_unauthorized_request = self.make_request(method, url,
                                headers=dict(Authorization='Bearer ' + 'random string'),
                                data=json.dumps(data)
                                )
                self.assertEqual(on_unauthorized_request.status_code, 403)
                unauthorized_request_response = json.loads(
                                                on_unauthorized_request.data.decode())
                self.assertEqual(unauthorized_request_response['message'],
                                    unauthorized_access_message)
        elif method in get_or_delete and isinstance(url, str):
            with self.app.app_context():
                # this does not need data to be anything but None
                # an error message is returned and a status code of 403
                on_unauthorized_request = self.make_request(method, url,
                                headers=dict(Authorization='Bearer ' + 'random string'))
                self.assertEqual(on_unauthorized_request.status_code, 403)
                unauthorized_request_response = json.loads(
                                                on_unauthorized_request.data.decode())
                self.assertEqual(unauthorized_request_response['message'],
                                    unauthorized_access_message)
        else:
            # after all the elif's if nothing matches, raise an error
            raise ValueError('The arguments are invalid for unauthorized request')

    def get_default_token(self):
        """
        A helper method to register and login a user 
        to get access token
        """
        with self.app.app_context():
            self.register_user()
            response = self.login_user()
            try:
                data_got = json.loads(response.data.decode())
                return data_got['access_token']
            except KeyError:
                raise KeyError('"access_token" is not a key. This is the data %s' % data_got)

    def create_shopping_list(self, access_token, shoppinglist_data=None):
        """
        A helper method to create a shopping list
        """
        if not shoppinglist_data:
            shoppinglist_data = self.shoppinglist_data
        with self.app.app_context():
            # create ShoppingList via post
            on_create = self.client().post('/shoppinglists/',
                        headers=dict(Authorization='Bearer ' + access_token),
                        data=json.dumps(shoppinglist_data)
                        )
            return json.loads(on_create.data.decode())['id'], on_create
            
    def make_get_request(self, url, access_token):
        """
        Helper method to make get requests
        """
        if url and access_token:
            with self.app.app_context():
                response = self.client().get(url, 
                headers=dict(Authorization="Bearer " + access_token))
                return response
        else:
            raise ValueError('Invalid arguments for make_get_request')