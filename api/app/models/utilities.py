"""
This module has functions used across different classes
"""

import re


def check_type(obj, type_object, *args, error_string='Invalid type'):
    """
    Checks the type of obj against the type_object
    and returns True is the same or else raises TypeError
    """
    if not isinstance(type_object, type):
        raise ValueError('second argument of check_type should be\
        a type not a %s')

    if isinstance(obj, type_object):
            return True

    arg_length = len(args)
    if arg_length > 0:
        for item in args:
            if isinstance(obj, item):
                return True

    raise TypeError(error_string)   


def check_email_format(email):
    """
    Checks that the email is in the right format with at
    least one @ and one period (.)
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError('Invalid email format')
    return True


def check_password_format(password, min_length=6):
    """
    Checks to ensure that the password is a string of not less
    than min_length
    """
    if check_type(password, str):
        if len(password) < min_length:
            raise ValueError("Your password is too short")
        return True
