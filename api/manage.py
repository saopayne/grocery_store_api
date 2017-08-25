"""
Script to help run migrations every time the models are changed
"""

import os
import unittest
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app


# initialize the app based on configurations
app = create_app (config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)
manager = Manager(app)

# create migration command
manager.add_command('db', MigrateCommand)

# create test command
@manager.command
def test():
    """
    Run the tests
    """
    # load the tests
    tests = unittest.TestLoader().discover('./test', pattern='test*.py')
    # run the tests
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


from app.models.shopping import User,ShoppingList, ShoppingItem

if __name__ == '__main__':
    manager.run()


