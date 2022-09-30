"""The applications config file."""
import os


class Config:
    """A class containing all the configuration variables used in app.py."""
    # flask
    FLASK_ENV = "development"
    TESTING = True
    SECRET_KEY = os.environ["SECRET_KEY"]
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
