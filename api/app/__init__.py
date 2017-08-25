""" This file has initialization code for the app """


from flask import Flask, request, jsonify, abort
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

    # register the auth blueprint
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app




