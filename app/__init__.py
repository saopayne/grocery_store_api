""" This file has initialization code for the app """

from flask import current_app
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

from app.authentication import get_authenticated_user
from app.models import utilities

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS,cross_origin

from configuration.config import APP_CONFIG

db = SQLAlchemy()


def create_app(config_name):
    """
    This is a wrapper for creation of the flask app
    based on the environment
    """
    app = Flask(__name__)
    app.config.from_object(APP_CONFIG[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SWAGGER'] = {
        'title': 'RideCo grocery store application'
    }
    db.init_app(app)
    CORS(app)

    @app.route('/grocerylists/', methods=['POST', 'GET'])
    def grocerylists():
        """
        For viewing and adding shopping lists
        """
        unauthorized_data = {'message': 'You do not have the appropriate permissions'}  # 403
        from app.authentication import get_authenticated_user
        user = get_authenticated_user(request)
        if isinstance(user, str):
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        if request.method == 'POST' and user:
            # create a shoppinglist
            # get json data even if content_type is not 'application/json'
            received_data = request.get_json(force=True)

            if received_data:
                # try to get the approriate values
                # expected {'title':'the title', 'description':'the description'}
                title = ''
                description = ''
                keys_of_receieved_data = received_data.keys()
                if 'title' in keys_of_receieved_data:
                    title = received_data['title']
                if 'description' in keys_of_receieved_data:
                    description = received_data['description']
                if len(title) > 0:
                    grocerylist = GroceryList(title=title, description=description,
                                              owner=user)
                    grocerylist.save()
                    response = jsonify({
                        'id': grocerylist.id,
                        'title': grocerylist.title,
                        'description': grocerylist.description
                    })
                    return make_response(response), 201

                else:
                    return make_response(jsonify(
                        {'message': 'The data you sent was in the wrong structure'})), 400
            else:
                return make_response(jsonify({'message': 'no data was sent'})), 400

        elif request.method == 'GET' and user:
            # view all the grocery lists for the user
            search_title = request.args.get('q') or None
            limit = request.args.get('limit') or None
            page = request.args.get('page') or None
            grocerylists_query = GroceryList.query.filter_by(owner=user)
            if search_title:
                search = '%' + search_title + '%'
                grocerylists_query = grocerylists_query.filter(GroceryList.title.ilike(search))
            grocerylists = grocerylists_query.all()
            if limit or page:
                # get the defaults if any of the args is None
                limit = limit or app.config['LISTS_PER_PAGE']
                page = page or 1
                # try to convert them to integers
                try:
                    limit = int(limit)
                    page = int(page)
                except ValueError:
                    return make_response(jsonify({'message':
                                                      'limit and page query parameters should be integers'})), 400
                # return an empty list if no grocery lists are found
                grocerylists = grocerylists_query.paginate(page, limit, False).items

            response = []
            for each_list in grocerylists:
                obj = {
                    'id': each_list.id,
                    'title': each_list.title,
                    'description': each_list.description
                }
                response.append(obj)
            return make_response(jsonify(response)), 200

    @app.route('/grocerylists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def single_grocerylist(id, **kwargs):
        """
        This route handles the view, edit and deletion of a grocerylist
        """
        unauthorized_data = {'message': 'You do not have the appropriate permissions'}  # 403
        non_existent_object = {'message': 'The shopping list does not exist'}
        from app.authentication import get_authenticated_user
        user = get_authenticated_user(request)
        if isinstance(user, str):
            # Has logged out
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        grocerylist = GroceryList.query.get(int(id))
        if not grocerylist:
            # shoppinglist does not exist
            return make_response(jsonify(non_existent_object)), 404

        if request.method == 'PUT' and grocerylist.owner == user:
            received_data = request.get_json(force=True)

            if received_data:
                keys_of_receieved_data = received_data.keys()

                if 'title' not in keys_of_receieved_data \
                        and 'description' not in keys_of_receieved_data:
                    return make_response(jsonify(
                        {'message': 'The data you sent was in the wrong structure'})), 400

                if 'title' in keys_of_receieved_data:
                    title = received_data['title']
                    if len(title) > 0:
                        # make sure the title is never blank
                        grocerylist.set_title(title)
                if 'description' in keys_of_receieved_data:
                    grocerylist.set_description(received_data['description'])
                # save the updated shopping list
                grocerylist.save()
                response = jsonify({
                    'id': grocerylist.id,
                    'title': grocerylist.title,
                    'description': grocerylist.description
                })
                return make_response(response), 200
            else:  # if  no data provided
                return make_response(jsonify({'message': 'no data was sent'})), 400

        if request.method == 'DELETE' and grocerylist.owner == user:
            # Delete the shoppinglist if it belongs to current user
            grocerylist.delete()
            return make_response(jsonify(
                {'message': 'Grocery list successfully deleted'})), 200

        if request.method == 'GET' and user:
            # Anyone authenticated is allowed to view these
            response = {
                'id': grocerylist.id,
                'title': grocerylist.title,
                'description': grocerylist.description
            }
            return make_response(jsonify(response)), 200

    @app.route('/grocerylists/<int:id>/items/', methods=['GET', 'POST'])
    @cross_origin()
    def all_items_of_grocerylist(id):
        unauthorized_data = {'message': 'You do not have the appropriate permissions'}  # 403
        non_existent_grocerylist = {'message': 'The grocery list does not exist'}
        user = get_authenticated_user(request)
        if isinstance(user, str):
            # Has logged out
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        grocerylist = GroceryList.query.get(int(id))
        if not grocerylist:
            return make_response(jsonify(non_existent_grocerylist)), 404
        if request.method == 'POST' and user:
            # get the data from the request
            received_data = request.get_json(force=True)

            if received_data:
                # try to get the approriate values
                # expected {'name':'the name', 'quantity':'the quantity', 
                # 'unit':'the unit'}
                name = ''
                quantity = 0
                unit = 'units'

                keys_of_receieved_data = received_data.keys()
                if 'name' in keys_of_receieved_data:
                    name = received_data['name']
                if 'quantity' in keys_of_receieved_data:
                    quantity = received_data['quantity']
                if 'unit' in keys_of_receieved_data:
                    unit = received_data['unit']
                if len(name) > 0:
                    groceryitem = GroceryItem(name=name, quantity=quantity,
                                              parent_list=grocerylist, unit=unit)
                    groceryitem.save()
                    response = jsonify({
                        'id': groceryitem.id,
                        'name': groceryitem.name,
                        'quantity': groceryitem.quantity,
                        'unit': groceryitem.unit
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return make_response(response), 201

                else:
                    return make_response(jsonify(
                        {'message': 'The data you sent was in the wrong structure'})), 400
            else:
                return make_response(jsonify({'message': 'no data was sent'})), 400

        if request.method == 'GET' and user:
            # get all the items that belong to the list
            # search and pagination
            search_name = request.args.get('q') or None
            limit = request.args.get('limit') or None
            page = request.args.get('page') or None
            grocery_items_query = GroceryItem.query.filter_by(parent_list=grocerylist)
            if search_name:
                search = '%' + search_name + '%'
                grocery_items_query = grocery_items_query.filter(GroceryItem.name.ilike(search))
            items = grocery_items_query.all()
            if limit or page:
                # get the defaults if any of the args is None
                limit = limit or app.config['ITEMS_PER_PAGE']
                page = page or 1
                # try to convert them to integers
                try:
                    limit = int(limit)
                    page = int(page)
                except ValueError:
                    return make_response(jsonify({'message':
                                                      'limit and page query parameters should be integers'})), 400
                items = grocery_items_query.paginate(page, limit, False).items
            response = []
            for item in items:
                obj = {
                    'id': item.id,
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit': item.unit
                }
                response.append(obj)
            return make_response(jsonify(response)), 200

    @app.route('/grocerylists/<int:id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    @cross_origin()
    def single_groceryitem(id, item_id):

        unauthorized_data = {'message': 'You do not have the appropriate permissions'}  # 403
        non_existent_grocery_list = {'message': 'The grocery list does not exist'}
        non_existent_grocery_item = {'message': 'The grocery item does not exist'}
        user = get_authenticated_user(request)
        if isinstance(user, str):
            # Has logged out
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        grocery_list = GroceryList.query.get(int(id))
        if not grocery_list:
            return make_response(jsonify(non_existent_grocery_list)), 404

        grocery_item = GroceryItem.query.get(int(item_id))
        if not grocery_item or not grocery_item.parent_list == grocery_list:
            return make_response(jsonify(non_existent_grocery_item)), 404

        if request.method == 'PUT' and grocery_list.owner == user:
            received_data = request.get_json(force=True)

            if received_data:
                name = ''
                quantity = '',
                unit = ''
                keys_of_receieved_data = received_data.keys()

                if 'name' not in keys_of_receieved_data and 'quantity' not in \
                        keys_of_receieved_data and 'unit' not in keys_of_receieved_data:
                    return make_response(jsonify(
                        {'message': 'The data you sent was in the wrong structure'})), 400

                if 'name' in keys_of_receieved_data:
                    name = received_data['name']
                    if len(name) > 0:
                        # make sure the name is never blank
                        grocery_item.set_name(name)
                if 'quantity' in keys_of_receieved_data:
                    grocery_item.set_quantity(received_data['quantity'])
                if 'unit' in keys_of_receieved_data:
                    grocery_item.set_unit(received_data['unit'])
                # save the updated shopping list
                grocery_item.save()
                response = {
                    'id': grocery_item.id,
                    'name': grocery_item.name,
                    'quantity': grocery_item.quantity,
                    'unit': grocery_item.unit
                }
                return make_response(jsonify(response)), 200
            else:  # if  no data provided
                return make_response(jsonify({'message': 'no data was sent'})), 400

        if request.method == 'DELETE' and grocery_list.owner == user:
            # only owners of the parent list are allowed to delete an item
            # attempt to delete the item
            grocery_item.delete()
            # send success message
            return make_response(jsonify(
                {'message': 'Grocery item successfully deleted'})), 200

        if request.method == 'GET' and user:
            # any one authenticated is allowed to view the items of the list
            # form the response object
            response = {
                'id': grocery_item.id,
                'name': grocery_item.name,
                'quantity': grocery_item.quantity,
                'unit': grocery_item.unit
            }
            # send the data
            return make_response(jsonify(response)), 200

    # register the auth blueprint
    from .authentication import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app


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
    grocery_lists = db.relationship('GroceryList', backref='owner',
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
        if utilities.check_type(name, str,
                                error_string="A user's name can only be a string"):
            self.name = name
            db.session.commit()

    def password_is_valid(self, password):
        return Bcrypt().check_password_hash(self.password, password)

    def set_username(self, username):
        if ' ' in username:
            raise ValueError('Username should have no space')
        if utilities.check_type(username, str,
                                error_string="A user's username can only be a string"):
            self.username = username
            db.session.commit()

    def set_email(self, email):
        if utilities.check_email_format(email):
            self.email = email
            db.session.commit()

    def set_password(self, password):
        self.password = password
        if utilities.check_password_format(password):
            self.password = Bcrypt().generate_password_hash(password).decode()
            db.session.commit()

    def create_grocery_list(self, title):
        """
        Creates a ShoppingList object whose creator attribute
        points to this user object
        """
        grocery_list = GroceryList(title, owner=self)
        grocery_list.save()
        return GroceryList.query.filter_by(title=title).first()

    def get_grocery_lists(self):
        """
        Get all the shopping lists that belong to the user
        """
        return GroceryList.query.filter_by(owner=self).all()

    def get_grocery_list_by_title(self, title):
        """
        Get the shopping list with the given title
        if it belongs to the user
        """
        shopping_list = None
        if utilities.check_type(title, str):
            shopping_list = GroceryList.query.filter_by(title=title, owner=self).first()
        return shopping_list

    def delete_shopping_list(self, grocery_list):
        if not isinstance(grocery_list, GroceryList):
            raise TypeError('Object is not a grocery list object')
        if not grocery_list.owner == self:
            raise KeyError('Grocery list does not exist')
        grocery_list.delete()

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
                algorithm='HS256'
            )

            return token
        except Exception as e:
            raise e

    @staticmethod
    def decode_token(token):
        """
        Function to decode the token when supplied
        """
        try:
            # decode using the app SECRET
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            is_blacklisted = BlacklistToken.check_blacklist(token)
            if is_blacklisted:
                return 'You are already logged out'
            return payload['sub']
        except:
            # in case the token is invalid
            # return 'Token is invalid. Try to login.'
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']

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


class GroceryList(db.Model):
    __tablename__ = 'grocerylist'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('GroceryItem', backref='parent_list',
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
        if utilities.check_type(title, str):
            self.title = title
            db.session.commit()

    def set_description(self, description):
        if utilities.check_type(description, str):
            self.description = description
            db.session.commit()

    def add_item(self, item_name):
        if utilities.check_type(item_name, str):
            grocery_item = GroceryItem(item_name, parent_list=self)
            grocery_item.save()
            return GroceryItem.query.filter_by(name=item_name, parent_list=self).first()

    def delete_item(self, item):
        if not isinstance(item, GroceryItem):
            raise TypeError('The item is of invalid type')
        if item.parent_list == self:
            item.delete()
        else:
            raise KeyError('The item does not exist')

    def get_grocery_items(self):
        return GroceryItem.query.filter_by(parent_list=self).all()

    def get_grocery_item_by_name(self, name):
        grocery_item = None
        if utilities.check_type(name, str):
            grocery_list = GroceryList.query.filter_by(name=name, parent_list=self).first()
        return grocery_item

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<GroceryList: %s>" % self.title


class GroceryItem(db.Model):
    __tablename__ = 'groceryitem'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(60))
    grocery_list_id = db.Column(db.Integer, db.ForeignKey('grocerylist.id'))

    def __init__(self, name, quantity=0, unit='', parent_list=None):  # , parent_list=None):
        # test that an item is never created parent_list = None
        if parent_list:
            if utilities.check_type(parent_list, GroceryList):
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
        if utilities.check_type(name, str):
            self.name = name
            db.session.commit()

    def set_unit(self, unit):
        if utilities.check_type(unit, str):
            self.unit = unit
            db.session.commit()

    def set_quantity(self, quantity):
        if utilities.check_type(quantity, float, int):
            self.quantity = float(quantity)
            db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<GroceryItem: %s>" % self.name


class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        if isinstance(token, bytes):
            # convert the bytes to string
            token = token.decode('utf-8')
        if utilities.check_type(token, str):
            # attempt to decode it
            user_id = User.decode_token(token)
            if not isinstance(user_id, str):
                self.token = token
            else:
                raise ValueError('The token should be valid')
        self.blacklisted_on = datetime.now()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            return str(e)

    @staticmethod
    def check_blacklist(token):
        """
        Check whether the token exists in the blacklist
        """
        if utilities.check_type(token, str):
            result = BlacklistToken.query.filter_by(token=token).first()
            if result:
                return True
            else:
                return False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
