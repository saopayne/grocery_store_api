"""
This includes the tests for the ShoppingItem model
"""


import unittest
from app.models.shopping import ShoppingItem
try:
    from .common_functions import BaseModelTestClass
except (ImportError, SystemError):
    from common_functions import BaseModelTestClass


class ShoppingItemModelTest(BaseModelTestClass):
    """
    All tests on the ShoppingItem model
    """

    def test_item_quantity_is_number(self):
        """
        An item quantity can only be a number of float or int type
        """
        self.assertRaises(TypeError, ShoppingItem, 
        'fruit', quantity='five', parent_list=self.shopping_list)
        self.assertRaises(TypeError, self.shopping_item.set_quantity,
            {'quantity':'float or int is expected, not dict'})

    def test_item_name_is_string(self):
        """
        An item name can only be a string
        """
        self.assertRaises(TypeError, ShoppingItem, 
        5, parent_list=self.shopping_list)
        self.assertRaises(TypeError, self.shopping_item.set_name,
            {'name':'string is expected, not dict'})
    
    def test_parent_is_shoppinglist(self):
        """
        On initialization, the parent_list argument should be of
        ShoppingList type and not None
        """
        with self.app.app_context():
            wrong_parent_list_type = 2
            self.assertRaises(TypeError, ShoppingItem, 'oranges', 5,
                        'units', parent_list=wrong_parent_list_type)
            self.assertRaises(ValueError, ShoppingItem, 'oranges', 5,
                        'units')

    def test_item_unit_is_string(self):
        """
        An item unit can only be a string
        """
        self.assertRaises(TypeError, ShoppingItem, 
        'fruit', unit=4, parent_list=self.shopping_list)
        self.assertRaises(TypeError, self.shopping_item.set_unit,
            {'unit':'string is expected, not dict'})

    def test_set_name(self):
        """
        the set_name method should set the name of the item
        """
        with self.app.app_context():
            new_name = 'vegetables'
            self.shopping_item.set_name(new_name)
            self.assertEqual(new_name, self.shopping_item.name)

    def test_set_quantity(self):
        """
        the set_quantity method should set the quantity of the item
        """
        with self.app.app_context():
            new_quantity = 40
            self.shopping_item.set_quantity(new_quantity)
            self.assertEqual(new_quantity, self.shopping_item.quantity)

    def test_set_unit(self):
        """
        the set_unit method should set the unit of the item
        """
        with self.app.app_context():
            new_unit = 'kg'
            self.shopping_item.set_unit(new_unit)
            self.assertEqual(new_unit, self.shopping_item.unit)
    

if __name__ == '__main__':
    unittest.main()

