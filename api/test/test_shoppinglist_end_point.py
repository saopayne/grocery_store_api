"""
This module is for running tests on all endpoints linking
to the ShoppingList model
"""

import unittest
import json
from app.models.shopping import User, ShoppingList
from .common_functions import ShoppingParentTestClass


class ShoppingListEndPointTest(ShoppingParentTestClass):
    """
    All endpoints directly interacting with the ShoppingList
    model are tested here
    """
    def delete_shopping_list(self, access_token, shoppinglist_id):
        """
        Helper method to delete a shopping list
        """
        if access_token and shoppinglist_id:
            with self.app.app_context():
                response = self.client().delete('shoppinglists/{}'.format(shoppinglist_id),
                headers=dict(Authorization="Bearer " + access_token))
                return response
        else:
            raise ValueError('Invalid arguments for delete_shopping_list')

    def test_shoppinglist_create(self):
        """
        Test that a ShoppingList object can be \
        created (POST) to /shoppinglists/
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create ShoppingList via post
            shoppinglist_id, on_create = self.create_shopping_list(access_token=access_token)
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
            shoppinglist_id, on_create_new_list = self.create_shopping_list(access_token,
                shoppinglist_data=original_list_data)
            self.assertEqual(on_create_new_list.status_code, 201)
            # get the id of the shopping list and edit it
            on_edit_list = self.client().put(
                '/shoppinglists/{}'.format(shoppinglist_id),
                headers=dict(Authorization="Bearer " + access_token),
                data=json.dumps(modified_list_data))
            self.assertEqual(on_edit_list.status_code, 200)
            # get the specified shopping list by id: assume this works fine
            modified_shopping_list = self.make_get_request(
                url='/shoppinglists/{}'.format(shoppinglist_id),
                access_token=access_token) 
            # convert the response to a dict
            modified_list_dict = json.loads(modified_shopping_list.data.decode())
            self.assertEqual(modified_list_data['title'],
                            modified_list_dict['title'])
            self.assertEqual(modified_list_data['description'],
                            modified_list_dict['description'])
            # test for invalid data
            invalid_data = {'name': 'It should be title not name'}
            self.invalid_data_request(url='/shoppinglists/{}'.\
                    format(shoppinglist_id), method='PUT',
                    invalid_data=invalid_data, access_token=access_token)
            # test for non-authorized request
            self.unauthorized_request(url='/shoppinglists/{}'.\
                    format(shoppinglist_id), method='PUT',
                    data={'title': 'New title'})

    def test_shoppinglist_delete(self):
        """
        Test that a ShoppingList object can be deleted
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create a shopping list
            shoppinglist_id, new_shopping_list = self.create_shopping_list(
                                                    access_token)
            self.assertEqual(new_shopping_list.status_code, 201)
            # show it exists by retrieving it by id
            shopping_list = self.make_get_request(
                url='/shoppinglists/{}'.format(shoppinglist_id),
                access_token=access_token)
            self.assertEqual(shopping_list.status_code, 200)
            # try deleting with no proper authentication. 403 is expected
            self.unauthorized_request(url='/shoppinglists/{}'.\
                    format(shoppinglist_id), method='DELETE')
            # delete it, return 200 ok status
            on_delete = self.delete_shopping_list(access_token=access_token,
                shoppinglist_id=shoppinglist_id)
            self.assertEqual(on_delete.status_code, 200)
            # show that it no longer exists, return 404 status
            shopping_list = self.make_get_request(
                url='/shoppinglists/{}'.format(shoppinglist_id),
                access_token=access_token)
            self.assertEqual(shopping_list.status_code, 404)
            # delete an object that doesn't exist, return 404 status
            on_delete = self.delete_shopping_list(access_token=access_token,
                shoppinglist_id=shoppinglist_id)
            self.assertEqual(on_delete.status_code, 404)

    def test_get_shoppinglist_by_id(self):
        """
        Test that a ShoppingList object can be got by id
        GET --> /shoppinglists/<id>
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create a new shopping list
            shoppinglist_id, on_create_list = self.create_shopping_list(
                                    access_token=access_token)
            self.assertEqual(on_create_list.status_code, 201)
            # get the shoppinglist
            single_list_response = self.make_get_request(
                url='/shoppinglists/{}'.format(shoppinglist_id),
                access_token=access_token)
            self.assertEqual(single_list_response.status_code, 200)
            # convert the data recieved into an dict
            retrieved_shopping_list = json.loads(single_list_response.data.decode())
            self.assertEqual(self.shoppinglist_data['title'],
                            retrieved_shopping_list['title'])
            # attempt to retrieve the data without proper authentication
            self.unauthorized_request(url='/shoppinglists/{}'.\
                format(shoppinglist_id), method='GET')

    def test_get_all_shoppinglists(self):
        """
        Test that all ShoppingList objects can be returned
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            # create a ShoppingList by making a POST request
            first_shoppinglist_id, first_shopping_list = self.create_shopping_list(
                                    access_token=access_token)
            self.assertEqual(first_shopping_list.status_code, 201)
            first_shopping_list_dict = json.loads(first_shopping_list.data.decode())
            # create another ShoppingList by making another POST request
            second_shoppinglist_id, second_shopping_list = self.create_shopping_list(
                        access_token=access_token, shoppinglist_data={'title': 'Academics'})
            self.assertEqual(second_shopping_list.status_code, 201)
            second_shopping_list_dict = json.loads(second_shopping_list.data.decode())        
            # get a list of all ShoppingLists that belong to the test user 
            # by making a GET request
            all_shopping_lists = self.make_get_request(
                url='/shoppinglists/', access_token=access_token) 
            all_shopping_lists_list = json.loads(all_shopping_lists.data.decode())
            self.assertEqual(all_shopping_lists.status_code, 200)
            self.assertIn(first_shopping_list_dict, all_shopping_lists_list)
            self.assertIn(second_shopping_list_dict, all_shopping_lists_list)        
            # test unauthenticated request and return 403
            self.unauthorized_request(url='/shoppinglists/', method='GET')
        

# Run the tests
if __name__ == "__main__":
    unittest.main()
