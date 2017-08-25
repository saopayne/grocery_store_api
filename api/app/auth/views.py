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

# register the view as part of the auth blueprint
registration_view = RegistrationView.as_view('register_view')
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST'])