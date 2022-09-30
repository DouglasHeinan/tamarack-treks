"""Creates the login_manager, to be used when initialising the app in app.py."""
from flask_login import LoginManager

login_manager = None


def create_login_manager(app):
    """Creates and initialises the login_manager."""
    global login_manager
    login_manager = LoginManager()
    login_manager.init_app(app)


