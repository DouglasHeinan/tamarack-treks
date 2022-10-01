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

    # mail
    MAIL_SERVER = "smtp.mail.yahoo.com"
    MAIL_PORT = 465
    MAIL_DEFAULT_SENDER = os.environ["EMAIL"]
    MAIL_PASSWORD = os.environ["EMAIL_PW"]
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
