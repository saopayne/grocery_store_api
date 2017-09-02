"""
The views for the auth blueprint
"""

from . import auth_blueprint

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models.shopping import User, BlacklistToken
import json
from flasgger import swag_from

    
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
        elif user_id == 'You are already logged out':
            return user_id
        else:
            return None

class RegistrationView(MethodView):
    """This class registers a new user at /auth/register"""

    @swag_from('docs/registration.yaml', methods=['POST'])
    def post(self):
        """Handle POST request for this view."""

        # get json data even if content_type is not 'application/json'
        received_data = request.get_json(force=True)
        invalid_data_message = {'message':'The data you sent was in the wrong structure'}
        user = None
        if received_data:
            # ensure the data is in approrpriate structure
            required_keys = ('username', 'name', 'password', 'email')
            if not all(key in received_data for key in required_keys):
                return make_response(jsonify(invalid_data_message)), 400
            # check if user exists
            user = User.query.filter_by(username=received_data['username']).first()
        else:
            return make_response(jsonify({'message':'no data was sent'})), 400
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

    @swag_from('docs/login.yaml', methods=['POST'])
    def post(self):
        """Handle POST request for this view."""

        # get json data even if content_type is not 'application/json'
        post_data = request.get_json(force=True)
        invalid_data_message = {'message':'The data you sent was in the wrong structure'}

        if post_data:
            # ensure the data is in approrpriate structure
            required_keys = ('username', 'password')
            if not all(key in post_data for key in required_keys):
                return make_response(jsonify(invalid_data_message)), 400
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


class LogoutView(MethodView):
    """
    This view handles logout at /auth/logout
    """

    @swag_from('docs/logout.yaml', methods=['POST'])
    def post(self):
        # get the atuhorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            access_token = None
        if access_token:
            token_response = User.decode_token(access_token)
            # if token is valid
            if not isinstance(token_response, str):
                # blacklist it
                blacklist_token = BlacklistToken(token=access_token)
                if isinstance(blacklist_token.save(), bool):
                    # it succeeded
                    response = {
                        'status': 'success',
                        'message': 'Logout successful'
                    }
                else:
                    # it has failed
                    response = {
                        'status': 'fail',
                        'message': 'Error logging out'
                    }
                return make_response(jsonify(response)), 200              
            else:
                # if decode_token returns a string
                response = {
                    'status': 'fail',
                    'message': token_response
                }
                return make_response(jsonify(response)), 401
        else:
            response = {
                'status': 'fail',
                'message': 'You do not have the appropriate permissions'
            }
            return make_response(jsonify(response)), 403 


class ResetPasswordView(MethodView):
    """
    View for resetting password on /auth/reset-password
    """

    @swag_from('docs/password_reset.yaml', methods=['POST'])
    def post(self):
        """
        View method for resetting password via a POST
        Expected payload {
            'old_password': 'what ever it is',
            'new_password': 'the new password'
        }
        """
        unauthorized_data = {'message':'You do not have the appropriate permissions'} # 403
        # check authentication
        user = get_authenticated_user(request)
        # if user is not authenticated
        if isinstance(user, str):
            return make_response(jsonify({'message': user})), 401
        if not user:
            # user not authenticated
            return make_response(jsonify(unauthorized_data)), 403
        else:
            # get the post_data received
            post_data = request.get_json(force=True)
            required_keys = ('old_password', 'new_password')
            if post_data:
                if not all(key in post_data for key in required_keys):
                    return make_response(jsonify(
                        {'message':'The data you sent was in the wrong structure',\
                         'details':'"old_password" and "new_password" are required keys'})), 400

                if user.password_is_valid(post_data['old_password']):
                    try:
                        user.set_password(post_data['new_password'])
                    except:
                        return make_response(jsonify({'message':'Password reset failed'})), 400
                    return make_response(jsonify({'message':'Password reset successful'})), 200
            else:
                return make_response(jsonify({'message':'no data was sent'})), 400

# register the view as part of the auth blueprint
registration_view = RegistrationView.as_view('register_view')
login_view = LoginView.as_view('login_view')
logout_view = LogoutView.as_view('logout_view')
reset_password_view = ResetPasswordView.as_view('reset_password_view')

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

# /auth/logout endpoint
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)

# /auth/reset-password
auth_blueprint.add_url_rule(
    '/auth/reset-password',
    view_func=reset_password_view,
    methods=['POST']
)