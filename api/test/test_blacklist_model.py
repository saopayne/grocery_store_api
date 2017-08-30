"""
Module for testing the Blacklist model
"""

import unittest
from app.models.shopping import BlacklistToken, ShoppingList
from .common_functions import BaseModelTestClass


class BlacklistModelTest(BaseModelTestClass):
    """
    Handles the testing for the Blacklist model class
    """
    
    def blacklist_token(self, token=None):
        """
        Helper method to blacklist a token
        """
        with self.app.app_context():
            if not token:
                # create token from default user
                token = self.user.generate_token(self.user.id)                   
            # blacklist token
            try:
                blacklisted_token = BlacklistToken(token=token)
                # putting save() commits to session and closes the session
                return blacklisted_token
            except Exception as e:
                raise e

    def test_token_can_be_blacklisted(self):
        """
        A token can be blacklisted
        """
        with self.app.app_context():
            blacklisted_token = self.blacklist_token()
            blacklisted_token.save() # save in the same session
            from_database = BlacklistToken.query.get(blacklisted_token.id)
            self.assertEqual(blacklisted_token.token, from_database.token)
    
    def test_token_is_string_or_bytes(self):
        """
        The token must be a string
        """
        with self.app.app_context():
            # try blacklisting a token that is an int
            self.assertRaises(TypeError, self.blacklist_token, token=76)
            self.assertRaises(TypeError, self.blacklist_token, token=True)
            self.assertRaises(TypeError, self.blacklist_token, token=
                            {'token':'should be string or bytes'})

    def test_token_can_be_searched_for(self):
        """
        Blacklisted token can be searched for and found
        """
        with self.app.app_context():
            blacklisted_token = self.blacklist_token()
            blacklisted_token.save() # save in the same session
            self.assertTrue(BlacklistToken.check_blacklist(blacklisted_token.token))

    def test_only_valid_tokens_allowed(self):
        """
        Only valid tokens should be blacklisted
        """
        with self.app.app_context():
            # try blacklisting a token that is an int
            self.assertRaises(ValueError, self.blacklist_token,
                             token='some random string')
            self.assertRaises(ValueError, self.blacklist_token,
                token='some random string to be converted to bytes'.encode('utf-8'))
