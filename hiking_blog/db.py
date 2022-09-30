"""Used in app.py when creating and initialising the database."""
from flask_sqlalchemy import SQLAlchemy

db = None


def instantiate_db(app):
    """Instantiates db and initialises the database."""
    global db
    db = SQLAlchemy()
    db.init_app(app)


def create_db():
    """Creates the database."""
    db.create_all()
