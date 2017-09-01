""" This file has initialization code for the app """


from flask import Flask, request, jsonify, abort, make_response
from flask_sqlalchemy import SQLAlchemy


# get the configurations
from configuration.config import APP_CONFIG

# initializing sqlalchemy
db = SQLAlchemy()


def create_app(config_name):
    """
    This is a wrapper for creation of the flask app
    based on the environment
    """
    app = Flask(__name__)
    app.config.from_object(APP_CONFIG[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from app.models.shopping import User, ShoppingList, \
        ShoppingItem, BlacklistToken
    from app.auth.views import get_authenticated_user
    
    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
        """
        Add a new shoppinglist or view all shoppinglists
        """
        unauthorized_data = {'message':'You do not have the appropriate permissions'} # 403
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
                    shoppinglist = ShoppingList(title=title, description=description,
                    owner=user)
                    shoppinglist.save()
                    response = jsonify({
                        'id': shoppinglist.id,
                        'title': shoppinglist.title,
                        'description': shoppinglist.description
                    })
                    return make_response(response), 201

                else:
                    return make_response(jsonify(
                        {'message':'The data you sent was in the wrong structure'})), 400
            else:
                return make_response(jsonify({'message':'no data was sent'})), 400

        elif request.method == 'GET' and user:
            # view all the shoppinglists
            search_title = request.args.get('q') or None
            limit = request.args.get('limit') or None
            page = request.args.get('page') or None
            shoppinglists_query = ShoppingList.query.filter_by(owner=user)  
            if search_title:             
                search = '%'+search_title+'%'
                shoppinglists_query = shoppinglists_query.filter(ShoppingList.title.ilike(search))
            shoppinglists = shoppinglists_query.all()
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
                # return an empty list if no shoppinglists are found
                shoppinglists = shoppinglists_query.paginate(page, limit, False).items

            response = []
            for each_list in shoppinglists:
                obj = {
                    'id': each_list.id,
                    'title': each_list.title,
                    'description': each_list.description
                }
                response.append(obj)
            return make_response(jsonify(response)), 200


    @app.route('/shoppinglists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def single_shoppinglist(id, **kwargs):
        """
        This route handles the view, edit and deletion of a shoppinglist
        """
        unauthorized_data = {'message':'You do not have the appropriate permissions'} # 403
        non_existent_object = {'message': 'The shopping list does not exist'}
        user = get_authenticated_user(request)
        if isinstance(user, str):
            # Has logged out
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        # try to get the shoping list
        shoppinglist = ShoppingList.query.get(int(id))
        if not shoppinglist:
            # shoppinglist does not exist
            return make_response(jsonify(non_existent_object)), 404

        if request.method == 'PUT' and shoppinglist.owner == user:
            received_data = request.get_json(force=True)

            if received_data:
                # try to get the approriate values
                # expected {'title':'the title', 'description':'the description'}
                title = ''
                description = ''
                keys_of_receieved_data = received_data.keys()

                if 'title' not in keys_of_receieved_data \
                    and 'description' not in keys_of_receieved_data:
                    return make_response(jsonify(
                            {'message':'The data you sent was in the wrong structure'})), 400

                if 'title' in keys_of_receieved_data:
                    title = received_data['title']
                    if len(title) > 0:
                        # make sure the title is never blank
                        shoppinglist.set_title(title)
                if 'description' in keys_of_receieved_data:
                    shoppinglist.set_description(received_data['description'])
                # save the updated shopping list
                shoppinglist.save()
                response = jsonify({
                        'id': shoppinglist.id,
                        'title': shoppinglist.title,
                        'description': shoppinglist.description
                })
                return make_response(response), 200
            else: # if  no data provided
                return make_response(jsonify({'message':'no data was sent'})), 400

        if request.method == 'DELETE' and shoppinglist.owner == user:
            # Delete the shoppinglist if it belongs to current user
            shoppinglist.delete()
            return make_response(jsonify(
                    {'message': 'Shopping list successfully deleted'})), 200
            
        if request.method == 'GET' and user:
            # Anyone authenticated is allowed to view these
            response = {
                'id': shoppinglist.id,
                'title': shoppinglist.title,
                'description': shoppinglist.description
            }
            return make_response(jsonify(response)), 200

    @app.route('/shoppinglists/<int:id>/items/', methods=['GET', 'POST'])
    def all_items_of_shoppinglist(id):
        """
        Route for viewing and and adding items to a shoppinglist
        """
        unauthorized_data = {'message':'You do not have the appropriate permissions'} # 403
        non_existent_shoppinglist = {'message': 'The shopping list does not exist'}
        user = get_authenticated_user(request)
        if isinstance(user, str):
            # Has logged out
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        # try to get the shoping list
        shoppinglist = ShoppingList.query.get(int(id))
        if not shoppinglist:
            # shoppinglist does not exist
            return make_response(jsonify(non_existent_shoppinglist)), 404
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
                    # the name should not be empty
                    # create the shoppingitem with the shoppinglist as the pasrent_list
                    shoppingitem = ShoppingItem(name=name, quantity=quantity,
                    parent_list=shoppinglist, unit=unit)
                    shoppingitem.save()
                    response = jsonify({
                        'id': shoppingitem.id,
                        'name': shoppingitem.name,
                        'quantity': shoppingitem.quantity,
                        'unit': shoppingitem.unit
                    })
                    return make_response(response), 201

                else:
                    return make_response(jsonify(
                        {'message':'The data you sent was in the wrong structure'})), 400
            else:
                return make_response(jsonify({'message':'no data was sent'})), 400

        if request.method == 'GET' and user:
            # get all the items that belong to the list
            search_name = request.args.get('q') or None
            if not search_name:
                items = shoppinglist.get_shopping_items()
            else:
                search = '%'+search_name+'%'
                items = ShoppingItem.query.filter_by(parent_list=shoppinglist).\
                                filter(ShoppingItem.name.ilike(search)).all()                
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

    @app.route('/shoppinglists/<int:id>/items/<int:item_id>',
     methods=['GET', 'PUT', 'DELETE'])
    def single_shoppingitem(id, item_id):
        """
        The route for editting, deleting, viewing a single shoppingitem
        """
        unauthorized_data = {'message':'You do not have the appropriate permissions'} # 403
        non_existent_shoppinglist = {'message': 'The shopping list does not exist'}
        non_existent_shoppingitem = {'message': 'The shopping item does not exist'}
        user = get_authenticated_user(request)
        if isinstance(user, str):
            # Has logged out
            return make_response(jsonify({'message': user})), 401
        if not user:
            # User is not authenticated
            return make_response(jsonify(unauthorized_data)), 403

        # try to get the shopping list
        shoppinglist = ShoppingList.query.get(int(id))
        if not shoppinglist:
            # shoppinglist does not exist
            return make_response(jsonify(non_existent_shoppinglist)), 404

        # try getting the shopping item
        shoppingitem = ShoppingItem.query.get(int(item_id))
        if not shoppingitem or not shoppingitem.parent_list == shoppinglist:
            return make_response(jsonify(non_existent_shoppingitem)), 404

        if request.method == 'PUT' and shoppinglist.owner == user:
            # only owners are allowed to edit the item
            # get the request data
            # update the shopping item
            received_data = request.get_json(force=True)

            if received_data:
                # try to get the approriate values
                # expected {'name':'the name', 'quantity':'the quantity', 'unit':'the unit'}
                name = ''
                quantity = '',
                unit = ''
                keys_of_receieved_data = received_data.keys()

                if 'name' not in keys_of_receieved_data and 'quantity' not in \
                    keys_of_receieved_data and 'unit' not in keys_of_receieved_data:
                    return make_response(jsonify(
                            {'message':'The data you sent was in the wrong structure'})), 400

                if 'name' in keys_of_receieved_data:
                    name = received_data['name']
                    if len(name) > 0:
                        # make sure the name is never blank
                        shoppingitem.set_name(name)
                if 'quantity' in keys_of_receieved_data:
                    shoppingitem.set_quantity(received_data['quantity'])
                if 'unit' in keys_of_receieved_data:
                    shoppingitem.set_unit(received_data['unit'])
                # save the updated shopping list
                shoppingitem.save()
                response = {
                    'id': shoppingitem.id,
                    'name': shoppingitem.name,
                    'quantity': shoppingitem.quantity,
                    'unit': shoppingitem.unit
                }
                return make_response(jsonify(response)), 200
            else: # if  no data provided
                return make_response(jsonify({'message':'no data was sent'})), 400

        
        if request.method == 'DELETE' and shoppinglist.owner == user:
            # only owners of the parent list are allowed to delete an item
            # attempt to delete the item
            shoppingitem.delete()
            # send success message
            return make_response(jsonify(
                    {'message': 'Shopping item successfully deleted'})), 200
        
        if request.method == 'GET' and user:
            # any one authenticated is allowed to view the items of the list
            # form the response object
            response = {
                'id': shoppingitem.id,
                'name': shoppingitem.name,
                'quantity': shoppingitem.quantity,
                'unit': shoppingitem.unit
            }
            # send the data
            return make_response(jsonify(response)), 200


    # register the auth blueprint
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app




