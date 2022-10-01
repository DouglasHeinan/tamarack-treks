"""Creates the mail object, to be used when initialising the app in app.py."""
from flask_mail import Mail

mail = None


def create_mail(app):
    """Creates and initialises the mail object"""
    global mail
    mail = Mail()
    mail.init_app(app)
