"""
This is the model file for shopping item
"""

from app import db
from app.models import utilities


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

    def __init__(self, name, quantity=0, unit=''): # , parent_list=None):
        if utilities.check_type(name, str):
            self.name = name
        if utilities.check_type(quantity, float, int):
            self.quantity = float(quantity)
        if utilities.check_type(unit, str):
            self.unit = unit
        # self.parent_list = parent_list

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
