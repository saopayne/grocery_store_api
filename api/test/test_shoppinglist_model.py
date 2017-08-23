"""
This includes the tests for the ShoppingList model
"""


import unittest
from app import create_app, db
from app.models.shopping import User, ShoppingList, ShoppingItem

class ShoppingListModelTest(unittest.TestCase):
    """
    All tests on the ShoppingList model plus a user object
    """
    def setUp(self):
        """
        Initialize the app, db
        """
        self.app = create_app(config_name='testing')
        with self.app.app_context():
            db.create_all()
            self.user = User('John Doe', 'john@example.com',
                                 'password', 'johndoe') 
            self.shopping_list = ShoppingList('Groceries',
                        'family daily grocery shopping list', owner=self.user)

    def test_owner_should_be_user(self):
        """
        On initialization, the owner argument should be of user type
        """
        with self.app.app_context():
            wrong_user_type = 2
            self.assertRaises(TypeError, ShoppingList, 'new groceries',
                        '', wrong_user_type)
            self.assertRaises(ValueError, ShoppingList, 'groceries')

    def test_title_is_string(self):
        """
        The title of the shopping list is 
        of type string (str) 
        """
        self.assertRaises(TypeError, ShoppingList, 
        5, 'A dummy description', self.user)
        self.assertRaises(TypeError, self.shopping_list.set_title,
            {'title':'string expected not dict'})

    def test_description_is_string(self):
        """
        The description of a shopping list is 
        of type string (str)
        """
        self.assertRaises(TypeError, ShoppingList, 
        'groceries', 55, self.user)
        self.assertRaises(TypeError, self.shopping_list.set_description,
            {'description':'string expected not dict'})

    def test_set_title(self):
        """
        The set_title method should set the title of
        the shopping list
        """
        with self.app.app_context():
            new_title = "party items"
            self.shopping_list.set_title(new_title)
            self.assertEqual(new_title, self.shopping_list.title)

    def test_set_description(self):
        """
        The set_description method should set the description of
        the shopping list
        """
        with self.app.app_context():
            new_description = "For Paul's birthday party"
            self.shopping_list.set_description(new_description)
            self.assertEqual(new_description,
                    self.shopping_list.description)

    def test_item_can_be_added(self):
        """
        An item can be added to the shopping list such that
        it becomes part of the list of items in the shopping list
        """
        with self.app.app_context():
            item_added = self.shopping_list.add_item('mangoes')
            shopping_list_items = ShoppingItem.query.filter_by(
                                  parent_list=self.shopping_list).all()
            self.assertIn(item_added, shopping_list_items)

    def test_an_item_can_be_deleted(self):
        """
        An item delete should only be deleted if it exists
        in the list of items of the shopping list

        The item should cease to exist in that list
        """
        with self.app.app_context():
            another_shopping_list = ShoppingList('Clothes',
                                'for the children', self.user)
            item_in_another_list = another_shopping_list.add_item('shirt')
            item_in_list = self.shopping_list.add_item('shirt')
            item_in_wrong_type = 8
            items_in_list = ShoppingItem.query.filter_by(parent_list=self.user).all()
            self.shopping_list.delete_item(item_in_list)
            self.assertRaises(KeyError, 
                    self.shopping_list.delete_item, item_in_another_list)
            self.assertRaises(TypeError, 
                    self.shopping_list.delete_item, item_in_wrong_type)
            self.assertNotIn(item_in_list, items_in_list)

        def test_get_shopping_items(self):
            """
            Tests that the get_shopping_items method returns all 
            the items of that shopping list
            """
            with self.app.app_context():
                first_shopping_item = self.shopping_list.add_item('sugar')
                second_shopping_item = self.shopping_list.add_item('bread')
                third_shopping_item = self.shopping_list.add_item('soda')
                all_items = self.shopping_list.get_shopping_items()
                self.assertIn(first_shopping_item, all_items)
                self.assertIn(second_shopping_item, all_items)
                self.assertIn(third_shopping_item, all_items)

        def test_get_shopping_item_by_name(self):
            """
            Tests that the get_shopping_item_by_name method works
            """
            with self.app.app_context():
                shopping_item = self.shopping_list.add_item('apples')
                self.assertEqual(shopping_item, self.user.get_shopping_item_by_name('apples'))


    def tearDown(self):
        """
        Do cleanup of test database
        """
        with self.app.app_context():
            db.session.remove
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
