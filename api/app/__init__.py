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

    from app.models.shopping import User, ShoppingList, ShoppingItem

    def get_authenticated_user(request):
        """
        Helper function to get the authenticated user based on 
        the token that is passed
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        access_token = auth_header.split(" ")[1]
        user = None
        if not access_token:
            return None
        else:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # user is authenticated so get the user
                user = User.query.get(user_id)
                return user
            else:
                return None

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
        """
        Add a new shoppinglist or view all shoppinglists
        """
        unauthorized_data = {'message':'You do not have the appropriate permissions'} # 403
        user = get_authenticated_user(request)
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
                return make_response(jsonify({'message':'no data was sent'}))

        elif request.method == 'GET' and user:
            # view all the shoppinglists
            shoppinglists = ShoppingList.query.filter_by(owner=user).all()
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
            
        if request.method == 'GET':
            # Anyone is allowed to view these
            response = {
                'id': shoppinglist.id,
                'title': shoppinglist.title,
                'description': shoppinglist.description
            }
            return make_response(jsonify(response)), 200


    # register the auth blueprint
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app




