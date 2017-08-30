"""
This module is for running tests on all endpoints linking
to the ShoppingItem model
"""

import unittest
import json
from app.models.shopping import User, ShoppingList, ShoppingItem
from .common_functions import ShoppingParentTestClass

# add tests for when user is logged out


class ShoppingItemEndPointTest(ShoppingParentTestClass):
    """
    All endpoints directly interacting with the ShoppingItem
    model are tested here
    """

    def create_shopping_item(self, access_token, shoppinglist_id, shoppingitem_data=None):
        """
        A helper method to create a shopping item
        """
        if not shoppingitem_data:
            shoppingitem_data = self.shoppingitem_data
        if isinstance(shoppinglist_id, int):
            with self.app.app_context():
                # create ShoppingList via post
                on_create = self.client().post('/shoppinglists/{}/items/'.\
                            format(shoppinglist_id),
                            headers=dict(Authorization='Bearer ' + access_token),
                            data=json.dumps(shoppingitem_data)
                            )
                return json.loads(on_create.data.decode())['id'], on_create
        else:
            raise ValueError('Invalid arguments for create_shopping_item')

    def delete_shopping_item(self, access_token, shoppinglist_id, item_id):
        """
        Helper method to delete a shopping item
        """
        if access_token and shoppinglist_id and item_id:
            with self.app.app_context():
                response = self.client().delete('shoppinglists/{}/items/{}'.format(shoppinglist_id,
                item_id), headers=dict(Authorization="Bearer " + access_token))
                return response
        else:
            raise ValueError('Invalid arguments for delete_shopping_item')

    def test_view_all_items(self):
        """
        All items of a shopping list can be viewed
        """
        with self.app.app_context():
            access_token = self.get_default_token()
            shoppinglist_id, on_create = self.create_shopping_list(access_token)
            self.assertEqual(on_create.status_code, 201)
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
            first_item_id, first_item_creation_response = self.create_shopping_item(
                access_token=access_token,shoppinglist_id=shoppinglist_id,
                shoppingitem_data=first_item_data)
            self.assertEqual(first_item_creation_response.status_code, 201)
            first_item_object = json.loads(first_item_creation_response.data.decode())
            # create second item
            second_item_id, second_item_creation_response = self.create_shopping_item(
                access_token=access_token,shoppinglist_id=shoppinglist_id,
                shoppingitem_data=second_item_data)
            self.assertEqual(second_item_creation_response.status_code, 201)
            second_item_object = json.loads(second_item_creation_response.data.decode())
            # check that the list of items returned has both items
            get_all_items_response = self.make_get_request(url='/shoppinglists/{}/items/'.\
                                            format(shoppinglist_id), access_token=access_token)
            self.assertEqual(get_all_items_response.status_code, 200)
            all_items = json.loads(get_all_items_response.data.decode())
            self.assertIn(first_item_object, all_items)
            self.assertIn(second_item_object, all_items)
            # check for unauthenticated requests
            self.unauthorized_request(url='/shoppinglists/{}/items/'.format(shoppinglist_id),
            method='GET')

    def test_view_and_add_single_item(self):
        """
        A single item in a shopping list can be viewed
        """
        with self.app.app_context():
            # create a shopping list
            access_token = self.get_default_token()
            shoppinglist_id, on_create = self.create_shopping_list(access_token)
            self.assertEqual(on_create.status_code, 201)
            # create a single item: assume this works fine
            item_id, item_creation_response = self.create_shopping_item(access_token=access_token,
                shoppinglist_id=shoppinglist_id)
            self.assertEqual(item_creation_response.status_code, 201)
            item_object = json.loads(item_creation_response.data.decode())
            # try to retrieve it
            item_created = self.make_get_request(url='shoppinglists/{}/items/{}'.\
                format(shoppinglist_id,item_id), access_token=access_token)
            # check that it exists
            self.assertEqual(item_created.status_code, 200)
            item_create_object = json.loads(item_created.data.decode())
            self.assertEqual(item_create_object['name'], self.shoppingitem_data['name'])
            self.assertEqual(item_create_object['quantity'], self.shoppingitem_data['quantity'])
            self.assertEqual(item_create_object['unit'], self.shoppingitem_data['unit'])
            # check for unauthenticated get requests
            self.unauthorized_request(url='/shoppinglists/{}/items/{}'.format(shoppinglist_id,
                item_id), method='GET') 
            # check for unauthenticate post request
            self.unauthorized_request(url='/shoppinglists/{}/items/'.format(shoppinglist_id), 
                method='POST', data=self.shoppingitem_data) 
            # check for invalid data post request
            invalid_data = {
                'title': 'this should be name'
            }
            self.invalid_data_request(url='/shoppinglists/{}/items/'.format(shoppinglist_id), 
                method='POST', invalid_data=invalid_data, access_token=access_token)  
            # test for logged out requests (POST and GET)
            self.make_logged_out_request(access_token=access_token, data=self.shoppingitem_data,
                url='/shoppinglists/{}/items/'.format(shoppinglist_id), method='POST')  
            self.make_logged_out_request(access_token=access_token,
                url='/shoppinglists/{}/items/{}'.format(shoppinglist_id, item_id), method='GET')
          
    def test_edit_item(self):
        """
        Editing the details of an item
        """
        with self.app.app_context():
            # create a shopping list
            access_token = self.get_default_token()
            shoppinglist_id, on_create = self.create_shopping_list(access_token)
            self.assertEqual(on_create.status_code, 201)
            # create a single item: assume this works fine
            item_id,item_creation_response = self.create_shopping_item(
                access_token=access_token, shoppinglist_id=shoppinglist_id)
            self.assertEqual(item_creation_response.status_code, 201)
            # try to editting it
            new_item = {
                'name': 'shoes',
                'quantity': 90,
                'unit': 'pairs'
            }
            item_modified_response = self.client().put('/shoppinglists/{}/items/{}'.\
                                            format(shoppinglist_id, item_id),
                                            headers=dict(Authorization='Bearer '+ access_token),
                                            data=json.dumps(new_item))
            self.assertEqual(item_modified_response.status_code, 200)
            # check that it is modified
            modified_item = json.loads(item_modified_response.data.decode())
            self.assertEqual(new_item['name'], modified_item['name'])
            self.assertEqual(new_item['quantity'], modified_item['quantity'])
            self.assertEqual(new_item['unit'], modified_item['unit'])
            # check for unauthenticated requests
            self.unauthorized_request(url='/shoppinglists/{}/items/{}'.\
                                            format(shoppinglist_id, item_id), 
                                            method='PUT', data=new_item)
            # check for invalid data requests
            self.invalid_data_request(url='/shoppinglists/{}/items/{}'.\
                format(shoppinglist_id, item_id), access_token=access_token,
                method='PUT', invalid_data={'title':'name not title'})
            # test a logged out request (PUT)
            self.make_logged_out_request(access_token=access_token, data=new_item,
                url='/shoppinglists/{}/items/{}'.format(shoppinglist_id, item_id),\
                method='PUT')  

        
    def test_delete_item(self):
        """
        Deleting an item in a shopping list
        """
        with self.app.app_context():
            # create a shopping list
            access_token = self.get_default_token()
            shoppinglist_id, on_create = self.create_shopping_list(access_token)
            self.assertEqual(on_create.status_code, 201)
            # create a single item: assume this works fine
            item_id, item_creation_response = self.create_shopping_item(
                access_token=access_token, shoppinglist_id=shoppinglist_id)
            self.assertEqual(item_creation_response.status_code, 201)
            # check that it exists
            item_created = self.make_get_request(url='shoppinglists/{}/items/{}'.format(shoppinglist_id,
                item_id), access_token=access_token)
            self.assertEqual(item_created.status_code, 200)
            # check for unauthenticated requests
            self.unauthorized_request(url='/shoppinglists/{}/items/{}'.\
                format(shoppinglist_id, item_id), method='DELETE')
            # try deleting it with appropriate authentication
            item_deleted_response = self.delete_shopping_item(access_token=access_token,
                shoppinglist_id=shoppinglist_id, item_id=item_id)
            self.assertEqual(item_deleted_response.status_code, 200)
            # check that it no longer exists
            item_deleted = self.make_get_request(url='shoppinglists/{}/items/{}'.format(shoppinglist_id,
                item_id), access_token=access_token)
            self.assertEqual(item_deleted.status_code, 404)
            # test a logged out request (PUT)
            self.make_logged_out_request(access_token=access_token,
                url='/shoppinglists/{}/items/{}'.format(shoppinglist_id, item_id),\
                method='DELETE')


# Run the tests
if __name__ == "__main__":
    unittest.main()
