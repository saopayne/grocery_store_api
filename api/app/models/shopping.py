"""
The module contains the following classes
 - User
 - ShoppingList
 - ShoppingItem
"""

from flask import current_app
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

from app import db
from app.models import utilities


class User(db.Model):
    """
    A User is the owner of shopping lists
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    shopping_lists = db.relationship('ShoppingList', backref='owner',
                                    lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, name, email, password, username):
        if utilities.check_type(name, str,
            error_string="A user's name can only be a string"):
             self.name = name
        if utilities.check_email_format(email):
            self.email = email
        if utilities.check_password_format(password):
            self.password = Bcrypt().generate_password_hash(password).decode()
        if utilities.check_type(username, str,
            error_string="A user's username can only be a string"):
             self.username = username

    def set_name(self, name):
        """
        Set the name of the user
        """
        if utilities.check_type(name, str,
             error_string="A user's name can only be a string"):
             self.name = name
             db.session.commit()

    def password_is_valid(self, password):
        """
        Checks whether the password passed matches with that on
        record
        """
        return Bcrypt().check_password_hash(self.password, password)

    def set_username(self, username):
        """
        Set the username of the user
        """
        if ' ' in username:
            raise ValueError('Username should have no space')
        if utilities.check_type(username, str,
             error_string="A user's username can only be a string"):
             self.username = username
             db.session.commit()
    
    def set_email(self, email):
        """
        Set the email of the User
        """
        if utilities.check_email_format(email):
            self.email = email
            db.session.commit()

    def set_password(self, password):
        """
        Sets the password of the user
        """
        self.password = password
        if utilities.check_password_format(password):
            self.password = Bcrypt().generate_password_hash(password).decode()
            db.session.commit()

    def create_shopping_list(self, title):
        """
        Creates a ShoppingList object whose creator attribute
        points to this user object
        """
        shopping_list = ShoppingList(title, owner=self)
        shopping_list.save()
        return ShoppingList.query.filter_by(title=title).first()

    def get_shopping_lists(self):
        """
        Get all the shopping lists that belong to the user
        """
        return ShoppingList.query.filter_by(owner=self).all()

    def get_shopping_list_by_title(self, title):
        """
        Get the shopping list with the given title
        if it belongs to the user
        """
        shopping_list = None
        if utilities.check_type(title, str):
            shopping_list = ShoppingList.query.filter_by(title=title, owner=self).first()
        return shopping_list

    def delete_shopping_list(self, shopping_list):
        """
        Allows user to delete a shopping
        list that they own
        """
        if not isinstance(shopping_list, ShoppingList):
            raise TypeError('Object is not a shopping list object')
        if not shopping_list.owner == self:
            raise KeyError('Shopping list does not exist')
        shopping_list.delete()

    def generate_token(self, user_id):
        """
        Generate the token for token-based auth
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=15),
                'iat': datetime.utcnow(),
                'sub': user_id
            }

            # create the token using the data above
            token = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algprithm='HS256'
            )

            return token
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        """
        Function to decode the token when supplied
        """
        try:
            # decode using the app SECRET
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # in case token is expired
            return 'Token has expired. Login again to receive new token.'
        except jwt.InvalidTokenError:
            # in case the token is invalid
            return 'Token is invalid. Try to login.'

    def save(self):
        """
        Saving to the database. After initialization, call this def
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return User.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<User: %s>" % self.username



class ShoppingList(db.Model):
    """
    A ShoppingList represents one shopping list
    It contains shopping items
    """
    __tablename__ = 'shoppinglist'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('ShoppingItem', backref='parent_list',
                            lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, title, description='', owner=None):
        # test to ensure a user is never None
        if owner:
            if utilities.check_type(owner, User):
                self.owner = owner
        if self.owner:
            if utilities.check_type(title, str):
                self.title = title
            if utilities.check_type(description, str):
                self.description = description
        else:
            raise ValueError('Invalid arguments')
        # self.items = []

    def set_title(self, title):
        """
        Sets the title of the shopping list
        """
        if utilities.check_type(title, str):
            self.title = title
            db.session.commit()

    def set_description(self, description):
        """
        Sets the description of the shopping list
        """
        if utilities.check_type(description, str):
            self.description = description
            db.session.commit()
    
    def add_item(self, item_name):
        """
        Adds an item to the list giving it the name
        item_name
        """
        if utilities.check_type(item_name, str):
            shopping_item = ShoppingItem(item_name, parent_list=self)
            shopping_item.save()
            return ShoppingItem.query.filter_by(name=item_name, parent_list=self).first()
    
    def delete_item(self, item):
        """
        Deletes an item from a shopping list
        """
        if not isinstance(item, ShoppingItem):
            raise TypeError('The item is of invalid type')
        if item.parent_list == self:
            item.delete()
        else:
            raise KeyError('The item does not exist')

    def get_shopping_items(self):
        """
        Get all the shopping items that belong to the list
        """
        return ShoppingItem.query.filter_by(parent_list=self).all()

    def get_shopping_item_by_name(self, name):
        """
        Get the shopping item with the given name
        if it belongs to the shopping list
        """
        shopping_item = None
        if utilities.check_type(name, str):
            shopping_list = ShoppingList.query.filter_by(name=name, parent_list=self).first()
        return shopping_item

    def save(self):
        """
        Saving to the database. After initialization, call this def
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<ShoppingList: %s>" % self.title


class ShoppingItem(db.Model):
    """
    A ShoppingItem represents a single item in 
    a shopping item
    """
    __tablename__ = 'shoppingitem'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(60))
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglist.id'))

    def __init__(self, name, quantity=0, unit='', parent_list=None): # , parent_list=None):
        # test that an item is nver created parent_list = None
        if parent_list:
            if utilities.check_type(parent_list, ShoppingList):
                self.parent_list = parent_list
        if self.parent_list:
            if utilities.check_type(name, str):
                self.name = name
            if utilities.check_type(quantity, float, int):
                self.quantity = float(quantity)
            if utilities.check_type(unit, str):
                self.unit = unit
        else:
            raise ValueError('Invalid arguments')

    def set_name(self, name):
        """
        Sets the name of the shopping list item
        """
        if utilities.check_type(name, str):
            self.name = name
            db.session.commit()

    def set_unit(self, unit):
        """
        Sets the unit of the shopping list item
        """
        if utilities.check_type(unit, str):
            self.unit = unit
            db.session.commit()

    def set_quantity(self, quantity):
        """
        Sets the quantity of the shopping list item
        """
        if utilities.check_type(quantity, float, int):
            self.quantity = float(quantity)
            db.session.commit()

    def save(self):
        """
        Saving to the database. After initialization, call this def
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<ShoppingItem: %s>" % self.name
