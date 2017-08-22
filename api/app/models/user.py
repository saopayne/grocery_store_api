"""
The model file for a User
"""

from app import db

class User(db.Model):
    """
    A User is the owner of shopping lists
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    shopping_lists = db.relationship('ShoppingList', backref='owner',
                                    lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, name, email, password, username):
        if utilities.check_type(name, str,
            error_string="A user's name can only be a string"):
             self.name = name
        if utilities.check_email_format(email):
            self.email = email
        if utilities.check_password_format(password):
            self.password = password
        if utilities.check_type(username, str,
            error_string="A user's username can only be a string"):
             self.username = username
        # self.shopping_lists = []

    def set_name(self, name):
        """
        Set the name of the user
        """
        if utilities.check_type(name, str,
             error_string="A user's name can only be a string"):
             self.name = name
             db.session.commit()

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
            self.password = password
            db.session.commit()

    def create_shopping_list(self, title):
        """
        Creates a ShoppingList object whose creator attribute
        points to this user object
        """
        pass
        #shopping_list = ShoppingList(title)
        #self.shopping_lists.append(shopping_list)
        #return shopping_list

    def delete_shopping_list(self, shopping_list):
        """
        Allows user to delete a shopping
        list that they own
        """
        #if not isinstance(shopping_list, ShoppingList):
        #    raise TypeError('Object is not a shopping list object')
        #if shopping_list not in self.shopping_lists:
        #    raise KeyError('Shopping list does not exist')
        # self.shopping_lists.remove(shopping_list)
        #shopping_list = None

    def save(self):
        """
        Saving to the database
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
