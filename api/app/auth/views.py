"""
The views for the auth blueprint
"""

from . import auth_blueprint

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models.shopping import User
import json

class RegistrationView(MethodView):
    """This class registers a new user at /auth/register"""

    def post(self):
        """Handle POST request for this view."""

        # get json data even if content_type is not 'application/json'
        received_data = request.get_json(force=True)
        user = None
        if received_data:
            # check if user exists
            user = User.query.filter_by(username=received_data['username']).first()
        else:
            return make_response(jsonify({'message':'no data was sent'}))
        # if not yet registered, attempt to register the user
        if not user:
            try:
                email = received_data['email']
                password = received_data['password']
                username = received_data['username']
                name = received_data['name']
                user = User(email=email, password=password,
                            name=name, username=username)
                user.save()

                response = {
                    'message': 'User registration successful'
                }
                # send success notification
                return make_response(jsonify(response)), 201
            except Exception as e:
                # catch any errors and give same response
                response = {
                    'message': 'Error while registering user. Try again'
                }
                return make_response(jsonify(response)), 401
        # if user is already registered
        else:
            response = {
                'message': 'User already exists. Please login'
            }

            return make_response(jsonify(response)), 202

class LoginView(MethodView):
    """
    This view handles user login and access token generation at auth/login
    """

    def post(self):
        """Handle POST request for this view."""

        # get json data even if content_type is not 'application/json'
        post_data = request.get_json(force=True)
        try:
            # Get the user object using their username
            user = User.query.filter_by(username=post_data['username']).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(post_data['password']):
                # Generate the access token to be used for future authentication
                access_token = user.generate_token(user.id)
                if access_token:
                    response = {
                        'message': 'Login successful',
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            else:
                # raise ValueError('this is the user %s' % str(user))
                # user does not exist or password is invalid
                response = {
                    'message': 'Invalid username or password. Try again'
                }
                return make_response(jsonify(response)), 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }
            # HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500


# register the view as part of the auth blueprint
registration_view = RegistrationView.as_view('register_view')
login_view = LoginView.as_view('login_view')

# /auth/register endpoint
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
    )

# /auth/login endpoint
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
    )