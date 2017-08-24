


import unittest
import app.models.utilities as utilities


class UtilitiesTests(unittest.TestCase):
    """
    Class to test the functionality of the functions
    in utilities.py
    """
    
    def test_check_type_return(self):
        """
        check_type returns True when the object is of any type in args
        check_type raises TypeError when the types are different
        check_type raises an error when the type_object is not a type        
        """
        self.assertTrue(utilities.check_type('girl', str))
        self.assertTrue(utilities.check_type('girl', float, int, str))
        self.assertRaises(TypeError, utilities.check_type, 5, bool)
        self.assertRaises(ValueError, utilities.check_type, 5, 9)
    
    def test_check_email_format(self):
        """
        check_email_formart returns True when email is right format
        check_email_format raises a ValueError when email format is wrong
        check_email_format raises a TypeError when email is not string
        """
        self.assertTrue(utilities.check_email_format('tom@example.com'))
        self.assertRaises(ValueError, utilities.check_email_format,
                        'tomexample.com')
        self.assertRaises(TypeError, utilities.check_email_format,
                        56)

    def test_check_password_format(self):
        """
        check_password_format returns True for a String of more characters
        check_password_format raises a ValueError when password string
        is of length less than min_length (default 6)
        check_password_format raises a TypeError when password is not string
        check_password_format raises a TypeError when min_length is not an int
        """
        self.assertTrue(utilities.check_password_format('rango679kiy'))
        self.assertRaises(ValueError, utilities.check_password_format, 'present',
                        10)
        self.assertRaises(TypeError, utilities.check_password_format, 43.5)
        self.assertRaises(TypeError, utilities.check_password_format, 'password',
                        '34r')


if __name__ == '__main__':
    unittest.main()