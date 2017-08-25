"""
This module is for running tests on all endpoints linking
to the ShoppingList model
"""

import unittest
from app.models.shopping import User, ShoppingList
import json
from app import create_app, db


class ShoppingListEndPointTest(unittest.TestCase):
    """
    All endpoints directly interacting with the ShoppingList
    model are tested here
    """
    def SetUp(self):
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
        user_data = {
            'username': username,
            'password': password
        }
        return self.client().post('/auth/login', 
                data=json.dumps(user_data))


# Run the tests
if __name__ == "__main__":
    unittest.main()
