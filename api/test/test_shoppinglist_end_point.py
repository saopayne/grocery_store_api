"""
This module is for running tests on all endpoints linking
to the ShoppingList model
"""

import unittest
import json
from app.models.shopping import User, ShoppingList
from app import create_app, db


class ShoppingListEndPointTest(unittest.TestCase):
    """
    All endpoints directly interacting with the ShoppingList
    model are tested here
    """
    
    def setUp(self):
        """
        Set up the db, the app and some variables
        """
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist_data = {'title': 'Groceries and Home stuff'}

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
        with app.app_context():
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
            with app.app_context():
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
        if method in get_or_delete and isinstance(url, str):
            with app.app_context():
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

    def test_shoppinglist_create(self):
        """
        Test that a ShoppingList object can be
        created (POST) to /shoppinglists/
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create ShoppingList via post
            on_create = self.client().post('/shoppinglists/',
                        headers=dict(Authorization='Bearer ' + access_token),
                        data=json.dumps(self.shoppinglist_data)
                        )
            self.assertEqual(on_create.status_code, 201)
            # on creation, the new list is returned
            new_shopping_list_details = json.loads(on_create.data.decode())
            self.assertEqual(self.shoppinglist_data['title'],
                            new_shopping_list_details['title'])
            # test for invalid data
            invalid_data = {'name':'There should be a title'}
            self.invalid_data_request(url='/shoppinglists/', method='POST',
            invalid_data=invalid_data, access_token=access_token)
            # test for unauthorized access
            self.unauthorized_request(url='/shoppinglists/', method='POST',
            data=self.shoppinglist_data)
            
    def test_shoppinglist_edit(self):
        """
        Test that a ShoppingList object can be edited
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            original_list_data = {'title': 'Food Stuffs'}
            modified_list_data = {
                                    "title": "Clothes",
                                    "description": "clothes for the kids"
                                }
            # create a new ShoppingList: assume this works fine
            on_create_new_list = self.client().post(
                '/shoppinglists/',
                headers=dict(Authorization="Bearer " + access_token),
                data=json.dumps(original_list_data))
            self.assertEqual(on_create_new_list.status_code, 201)
            new_shopping_list_details = json.loads(on_create_new_list.data.decode())
            # get the id of the shopping list and edit it
            on_edit_list = self.client().put(
                '/shoppinglists/{}'.format(new_shopping_list_details['id']),
                headers=dict(Authorization="Bearer " + access_token),
                data=json.dumps(modified_list_data))
            self.assertEqual(on_edit_list.status_code, 200)
            # get the specified shopping list by id: assume this works fine
            modified_shopping_list = self.client().get(
                '/shoppinglists/{}'.format(on_create['id']),
                headers=dict(Authorization="Bearer " + access_token))
            # convert the response to a dict
            modified_list_dict = json.loads(modified_shopping_list.data.decode())
            self.assertEqual(modified_list_data['title'],
                            modified_list_dict['title'])
            self.assertEqual(modified_list_data['description'],
                            modified_list_dict['description'])
            # test for invalid data
            invalid_data = {'name': 'It should be title not name'}
            self.invalid_data_request(url='/shoppinglists/{}'.\
                    format(new_shopping_list_details['id']), method='PUT',
                    invalid_data=invalid_data, access_token=access_token)
            # test for non-authorized request
            self.unauthorized_request(url='/shoppinglists/{}'.\
                    format(new_shopping_list_details['id']), method='PUT',
                    data={'title': 'New title'})

    def test_shoppinglist_delete(self):
        """
        Test that a ShoppingList object can be deleted
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create a shopping list
            new_shopping_list = self.client().post('/shoppinglists/',
                                headers=dict(Authorization="Bearer " + access_token),
                                data=json.dumps(self.shoppinglist_data))
            self.assertEqual(new_shopping_list.status_code, 201)
            new_shopping_list_dict = json.loads(new_shopping_list.data.decode())
            # show it exists by retrieving it by id
            shopping_list = self.client().get(
                '/shoppinglist/{}'.format(new_shopping_list_dict['id']),
                headers=dict(Authorization="Bearer " + access_token))
            self.assertEqual(shopping_list.status_code, 200)
            # try deleting with no proper authentication. 403 is expected
            self.unauthorized_request(url='/shoppinglist/{}'.\
                    format(new_shopping_list_dict['id']), method='DELETE')
            # delete it, return 200 ok status
            on_delete = self.client().delete(
                '/shoppinglist/{}'.format(new_shopping_list_dict['id']),
                headers=dict(Authorization="Bearer " + access_token))
            self.assertEqual(on_delete.status_code, 200)
            # show that it no longer exists, return 404 status
            shopping_list = self.client().get(
                '/shoppinglist/{}'.format(new_shopping_list_dict['id']),
                headers=dict(Authorization="Bearer " + access_token))
            self.assertEqual(shopping_list.status_code, 404)
            # delete an object that doesn't exist, return 404 status
            on_delete = self.client().delete(
                '/shoppinglist/{}'.format(new_shopping_list_dict['id']),
                headers=dict(Authorization="Bearer " + access_token))
            self.assertEqual(on_delete.status_code, 404)

    def test_get_shoppinglist_by_id(self):
        """
        Test that a ShoppingList object can be got by id
        GET --> /shoppinglists/<id>
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create a new shopping list
            on_create_list = self.client().post(
                '/shoppinglists/',
                headers=dict(Authorization="Bearer " + access_token),
                data=json.dumps(self.shoppinglist_data))
            self.assertEqual(on_create_list.status_code, 201)
            # convert the data received to dict
            new_shopping_list_details = json.loads(on_create_list.data.decode())
            single_list_response = self.client().get(
                '/shoppinglist/{}'.format(new_shopping_list_details['id']),
                headers=dict(Authorization="Bearer " + access_token))
            self.assertEqual(single_list_response.status_code, 200)
            # convert the data recieved into an dict
            retrieved_shopping_list = json.loads(single_list_response.data.decode)
            self.assertEqual(self.shoppinglist_data['title'],
                            retrieved_shopping_list['title'])
            # attempt to retrieve the data without proper authentication
            self.unauthorized_request(url='/shoppinglist/{}'.\
                format(new_shopping_list_details['id']), method='GET')

    def test_get_all_shoppinglists(self):
        """
        Test that all ShoppingList objects can be returned
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create a ShoppingList by making a POST request
            first_shopping_list = self.client().post(
                '/shoppinglists/',
                headers=dict(Authorization="Bearer " + access_token),
                data=json.dumps(self.shoppinglist_data))
            self.assertEqual(first_shopping_list.status_code, 201)
            first_shopping_list_dict = json.loads(first_shopping_list.data.decode)
            # create another ShoppingList by making another POST request
            second_shopping_list = self.client().post(
                '/shoppinglists/',
                headers=dict(Authorization="Bearer " + access_token),
                data=json.dumps({'title': 'Academics'}))
            self.assertEqual(second_shopping_list.status_code, 201)
            second_shopping_list_dict = json.loads(second_shopping_list.data.decode)        
            # get a list of all ShoppingLists that belong to the test user 
            # by making a GET request
            all_shopping_lists = self.client().get(
                '/shoppinglists/',
                headers=dict(Authorization="Bearer " + access_token),
            )
            all_shopping_lists_list = json.loads(all_shopping_lists.data.decode)
            self.assertEqual(all_shopping_lists.status_code, 200)
            self.assertIn(first_shopping_list_dict, all_shopping_lists_list)
            self.assertIn(second_shopping_list_dict, all_shopping_lists_list)        
            # test unauthenticated request and return 403
            self.unauthorized_request(url='/shoppinglists/', method='GET')

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
        

# Run the tests
if __name__ == "__main__":
    unittest.main()
