"""
File to initialize the auth Blueprint
This is to make the app more modular
"""

from flask import Blueprint


auth_blueprint = Blueprint('auth', __name__)

from . import views