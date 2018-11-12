"""
This is the entry point for the app
"""

import os
from app import create_app, User, GroceryList
from app import db

config_name = os.getenv('APP_SETTINGS') or 'development'
app = create_app(config_name)

with app.app_context():
    db.create_all()
    # Create a mock user to use for the demo
    user = User.query.filter_by(id=1).first()
    grocery_list = GroceryList.query.filter_by(id=1).first()
    if user is None:
        user = User(name='Ademola Oyewale', email='saopayne@gmail.com', password='sample', username='sao')
        user.save()
    if grocery_list is None:
        grocery_list = GroceryList(title='Demo List One', description='This list contains demo grocery items', owner=user)
        grocery_list.save()

if __name__ == '__main__':
    app.run()
