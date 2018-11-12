"""
This is where the configurations of the app are found \
"""

import os


class Config(object):
    """
    This is the parent configurations to be inherited from
    """
    DEBUG = False
    SECRET = os.getenv('SECRET')
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.getenv('RIDECO_DATABASE_URL')
    LISTS_PER_PAGE = os.getenv('LISTS_PER_PAGE') or 6
    ITEMS_PER_PAGE = os.getenv('ITEMS_PER_PAGE') or 10


class DevelopmentConfig(Config):
    """
    The configuration for the development environment
    """
    DEBUG = True
    SECRET = "development secret"
    SQLALCHEMY_DATABASE_URI = os.getenv('RIDECO_DATABASE_URL') or \
                              "mysql://root:saopayne@localhost:3306/rideco_grocery_db"


class TestingConfig(Config):
    DEBUG = True
    SECRET = "development secret"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('RIDECO_TEST_DATABASE_URL') or \
                              "mysql://root:saopayne@localhost:3306/rideco_grocery_test_db"


class StagingConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


APP_CONFIG = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
}
