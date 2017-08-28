"""
This module is for running tests on all endpoints linking
to the ShoppingItem model
"""

import unittest
import json
from app.models.shopping import User, ShoppingList, ShoppingItem
from app import create_app, db


class ShoppingItemEndPointTest(unittest.TestCase):
    """
    All endpoints directly interacting with the ShoppingItem
    model are tested here
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

    def create_shopping_list(self, access_token, title='Groceries',
        description='Groceries and Home stuff'):
        """
        A helper method to create a shopping list
        """
        with self.app.app_context():
            # create ShoppingList via post
            on_create = self.client().post('/shoppinglists/',
                        headers=dict(Authorization='Bearer ' + access_token),
                        data=json.dumps(self.shoppinglist_data)
                        )
            return json.loads(on_create.data.decode())['id']


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
                raise KeyError('"access_token" is not a key. This is the data %s'\
                     % data_got)

    def test_view_all_items(self):
        """
        All items of a shopping list can be viewed
        """
        access_token = self.get_default_token()
        shoppinglist_id = self.create_shopping_list(access_token)
        first_item_data = {
            'name': 'guavas',
            'quantity': 7,
            'unit': 'baskets'
        }
        second_item_data = {
            'name': 'oranges',
            'quantity': 17,
            'unit': 'units'
        }
        # create first item
        first_item_creation_response = self.client().post('/shoppinglists/{}/items/'.\
                                        format(shoppinglist_id),
                                        headers=dict(Authorization='Bearer '+ access_token),
                                        data=json.dumps(first_item_data))
        self.assertEqual(first_item_creation_response.status_code, 201)
        first_item_object = json.loads(first_item_creation_response.data.decode())
        # create second item
        second_item_creation_response = self.client().post('/shoppinglists/{}/items/'.\
                                        format(shoppinglist_id),
                                        headers=dict(Authorization='Bearer '+ access_token),
                                        data=json.dumps(second_item_data))
        self.assertEqual(second_item_creation_response.status_code, 201)
        second_item_object = json.loads(second_item_creation_response.data.decode())
        # check that the list of items returned has both items
        get_all_items_response = self.client().get('/shoppinglists/{}/items/'.\
                                        format(shoppinglist_id),
                                        headers=dict(Authorization='Bearer '+ access_token))
        self.assertEqual(get_all_items_response.status_code, 200)
        all_items = json.loads(get_all_items_response.data.decode())
        self.assertIn(first_item_object, all_items)
        self.assertIn(second_item_object, all_items)
        # check for unauthenticated requests
        self.unauthorized_request(url='/shoppinglists/{}/items'.format(shoppinglist_id),
        method='GET')

    def test_view_and_add_single_item(self):
        """
        A single item in a shopping list can be viewed
        """
        # create a shopping list
        access_token = self.get_default_token()
        shoppinglist_id = self.create_shopping_list(access_token)
        # create a single item: assume this works fine
        item_creation_response = self.client().post('/shoppinglists/{}/items/'.\
                                        format(shoppinglist_id),
                                        headers=dict(Authorization='Bearer '+ access_token),
                                        data=json.dumps(self.shoppingitem_data))
        self.assertEqual(item_creation_response.status_code, 201)
        item_object = json.loads(item_creation_response.data.decode())
        # try to retrieve it
        item_created = self.client().get('shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), headers=dict(Authorization="Bearer " + access_token))
        # check that it exists
        self.assertEqual(item_created.status_code, 200)
        item_create_object = json.loads(item_created.data.decode())
        self.assertEqual(item_create_object['name'], self.shoppingitem_data['name'])
        self.assertEqual(item_create_object['quantity'], self.shoppingitem_data['quantity'])
        self.assertEqual(item_create_object['unit'], self.shoppingitem_data['unit'])
        # check for unauthenticated get requests
        self.unauthorized_request(url='/shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), method='GET') 
        # check for unauthenticate post request
        self.unauthorized_request(url='/shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), method='POST', data=self.shoppingitem_data) 
        # check for invalid data post request
        invalid_data = {
            'title': 'this should be name'
        }
        self.invalid_data_request(url='/shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), method='POST', invalid_data=invalid_data, access_token=access_token)      
        
    def test_edit_item(self):
        """
        Editing the details of an item
        """
        # create a shopping list
        access_token = self.get_default_token()
        shoppinglist_id = self.create_shopping_list(access_token)
        # create a single item: assume this works fine
        item_creation_response = self.client().post('/shoppinglists/{}/items/'.\
                                        format(shoppinglist_id),
                                        headers=dict(Authorization='Bearer '+ access_token),
                                        data=json.dumps(self.shoppingitem_data))
        self.assertEqual(item_creation_response.status_code, 201)
        item_object = json.loads(item_creation_response.data.decode())
        # try to editting it
        new_item = {
            'name': 'shoes',
            'quantity': 90,
            'unit': 'pairs'
        }
        item_modified_response = self.client().put('/shoppinglists/{}/items/{}'.\
                                        format(shoppinglist_id, item_object['id']),
                                        headers=dict(Authorization='Bearer '+ access_token),
                                        data=json.dumps(new_item))
        self.assertEqual(item_modified_response.status_code, 201)
        # check that it is modified
        modified_item = json.loads(item_modified_response.data.decode())
        self.assertEqual(new_item['name'], modified_item['name'])
        self.assertEqual(new_item['quantity'], modified_item['quantity'])
        self.assertEqual(new_item['unit'], modified_item['unit'])
        # check for unauthenticated requests
        self.unauthorized_request(url='/shoppinglists/{}/items/{}'.\
                                        format(shoppinglist_id, item_object['id']), 
                                        method='PUT', data=new_item)
        # check for invalid data requests
        self.invalid_data_request(url='/shoppinglists/{}/items/{}'.\
            format(shoppinglist_id, item_object['id']), access_token=access_token,
            method='PUT', invalid_data={'title':'name not title'})
        
    def test_delete_item(self):
        """
        Deleting an item in a shopping list
        """
        # create a shopping list
        access_token = self.get_default_token()
        shoppinglist_id = self.create_shopping_list(access_token)
        # create a single item: assume this works fine
        item_creation_response = self.client().post('/shoppinglists/{}/items/'.\
                                        format(shoppinglist_id),
                                        headers=dict(Authorization='Bearer '+ access_token),
                                        data=json.dumps(self.shoppingitem_data))
        self.assertEqual(item_creation_response.status_code, 201)
        item_object = json.loads(item_creation_response.data.decode())
        # check that it exists
        item_created = self.client().get('shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(item_created.status_code, 200)
        # check for unauthenticated requests
        self.unauthorized_request(url='/shoppinglists/{}/items/{}'.\
            format(shoppinglist_id, item_object['id']), method='DELETE')
        # try deleting it with appropriate authentication
        item_deleted_response = self.client().delete('shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(item_deleted_response.status_code, 200)
        # check that it no longer exists
        item_deleted = self.client().get('shoppinglists/{}/items/{}'.format(shoppinglist_id,
            item_object['id']), headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(item_deleted.status_code, 404)


# Run the tests
if __name__ == "__main__":
    unittest.main()
