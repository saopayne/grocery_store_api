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
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class DevelopmentConfig(Config):
    """
    The configuration for the development environment
    """
    DEBUG = True
    SECRET = "development secret"
    SQLALCHEMY_DATABASE_URI = "postgresql://startups:pass@localhost:5432/shopping_db"


class TestingConfig(Config):
    """
    The configuration for testing
    """
    DEBUG = True
    SECRET = "development secret"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://startups:pass@localhost:5432/shopping_test_db"

class StagingConfig(Config):
    """
    The configuration for staging
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Extra configuration for Production
    """
    DEBUG = False
    TESTING = False


APP_CONFIG = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
}
