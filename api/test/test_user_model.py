"""
This includes the tests for the user model
"""


import unittest
from app import create_app, db
from app.models.shopping import User, ShoppingList, ShoppingItem


class UserModelTest(unittest.TestCase):
    """
    All tests on the user model plus a user object
    """
    def setUp(self):
        """
        Initialize the app db
        """
        self.app = create_app(config_name='testing')
        self.user = User('John Doe', 'john@example.com',
                                 'password', 'johndoe') 

        with self.app.app_context():
            db.create_all()

    def test_user_name_is_string(self):
        """
        A user's name can only be a string
        """
        self.assertRaises(TypeError, User, 5, 
                        'john@example.com', 'password', 'johndoe')
        self.assertRaises(TypeError, self.user.set_name, 5)

    def test_user_username_is_string(self):
        """
        A user's username can only be a string and has no space
        """
        self.assertRaises(TypeError, User, 'John Doe', 
                        'john@example.com', 'password', 5 )
        self.assertRaises(TypeError, self.user.set_username, 5)
        self.assertRaises(ValueError, self.user.set_username,
             'Adam scott')

    def test_user_email_format(self):
        """
        An email should have only one @ and . and is a string
        """
        self.assertRaises(ValueError, User, 'John Doe',
            'johnexample.com', 'password', 'johndoe')
        self.assertRaises(ValueError, User, 'John Doe',
            'john@examplecom', 'password', 'johndoe')
        self.assertRaises(TypeError, User, 'John Doe',
            6, 'password')
        self.assertRaises(ValueError, self.user.set_email,
            'johnexample.com')

    def test_user_password_length(self):
        """
        A user's password should be at least 6 characters long
        and is a string
        """
        self.assertRaises(ValueError, User, 'John Doe',
            'john@example.com', 'pas', 'johndoe')
        self.assertRaises(TypeError, User, 'John Doe',
            'john@example.com', 5, 'johndoe')
        self.assertRaises(ValueError, self.user.set_password,
            'pas')
        self.assertRaises(TypeError, self.user.set_password,
            5)

    def test_set_name(self):
        """
        the set_name method should set the name of the user
        """
        new_name = 'Tori Doe'
        with self.app.app_context():
            self.user.set_name(new_name)
            self.assertEqual(new_name, self.user.name)

    def test_set_username(self):
        """
        the set_username method should set the username of the user
        """
        new_username = 'joriun'
        with self.app.app_context():
            self.user.set_username(new_username)
            self.assertEqual(new_username, self.user.username)

    def test_set_email(self):
        """
        the set_email method should set the email of the user
        """
        new_email = 'tori@example.com'
        with self.app.app_context():
            self.user.set_email(new_email)
            self.assertEqual(new_email, self.user.email)

    def test_set_password(self):
        """
        the set_password method should set the password of the user
        """
        new_password = 'password123'
        with self.app.app_context():
            old_password = self.user.password
            self.user.set_password(new_password)
            self.assertTrue(self.user.password_is_valid(new_password))
            self.assertFalse(self.user.password_is_valid(old_password))

    def test_user_create_shoppinglist(self):
        """
        A user should be able to create a shopping list and add it to the
        his/her list of shopping lists
        """
        with self.app.app_context():
            shopping_list = self.user.create_shopping_list('groceries')
            self.assertIn(shopping_list, self.user.shopping_lists)

    def test_user_delete_shopping_list(self):
        """
        A user can delete his/her own shoppinglist
        and it should cease to exist
        It should exist in his/her lists before it is deleted

        the shopping list  must be an instance of ShoppingList class
        """
        with self.app.app_context():
            user2 = User('Tom Doe', 'tom@example.com', 'password', 'tomdoe')
            user_2_shopping_list = user2.create_shopping_list('hoilday shopping')
            user_shopping_list = self.user.create_shopping_list('groceries')
            third_shopping_list = 3
            self.assertRaises(KeyError, self.user.delete_shopping_list,
                            user_2_shopping_list)
            self.user.delete_shopping_list(user_shopping_list)
            self.assertNotIn(user_shopping_list, self.user.shopping_lists)
            self.assertRaises(TypeError, self.user.delete_shopping_list,
                            third_shopping_list)

    def test_get_shopping_lists(self):
        """
        Test that all the shopping lists that belong to the user
        are returned
        """
        with self.app.app_context():
            first_shopping_list = self.user.create_shopping_list('groceries')
            second_shopping_list = self.user.create_shopping_list('birthday')
            third_shopping_list = self.user.create_shopping_list('office party')
            all_lists = self.user.get_shopping_lists()
            self.assertIn(first_shopping_list, all_lists)
            self.assertIn(second_shopping_list, all_lists)
            self.assertIn(third_shopping_list, all_lists)

    def test_get_shopping_list_by_title(self):
        """
        Test that a shopping list can be returned with get_shopping_list_by_title
        """
        with self.app.app_context():
            shopping_list = self.user.create_shopping_list('groceries')
            self.assertEqual(shopping_list, self.user.get_shopping_list_by_title('groceries'))

    def tearDown(self):
        """
        Do cleanup of test database
        """
        with self.app.app_context():
            db.session.remove
            db.drop_all()


if __name__ == '__main__':
    unittest.main()

    