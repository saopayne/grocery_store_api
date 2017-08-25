"""
This is the entry point for the app
"""

import os
from app import create_app
from app.models.shopping import db

config_name = os.getenv('APP_SETTINGS') or 'development'
app = create_app(config_name)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()