from flask_login import LoginManager

login_manager = None


def create_login_manager(app):
    global login_manager
    login_manager = LoginManager()
    login_manager.init_app(app)


