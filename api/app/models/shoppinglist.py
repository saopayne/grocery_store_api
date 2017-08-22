"""
This is the model file for shopping list
"""

from app import db
from app.models import utilities


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

    def __init__(self, title, description=''):
        if utilities.check_type(title, str):
            self.title = title
        if utilities.check_type(description, str):
            self.description = description
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
        pass
        # item = ShoppingItem(item_name)
        # self.items.append(item)
        # return item

    def delete_item(self, item):
        """
        Deletes an item from a shopping list
        """
        pass
        # if not isinstance(item, ShoppingItem):
        #    raise TypeError('The item is of invalid type')
        # if item in self.items:
        #    self.items.remove(item)
        # else:
        #    raise KeyError('The item does not exist')

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

