from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap


db = SQLAlchemy()
login_manager = LoginManager()
ckeditor = CKEditor()
bootstrap = Bootstrap()


def init_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    with app.app_context():
        from .home import dashboard
        from .gear import gear
        from .trails import trails
        from . import contact, auth

        app.register_blueprint(dashboard.home_bp)
        app.register_blueprint(gear.gear_bp)
        app.register_blueprint(trails.trail_bp)
        app.register_blueprint(contact.contact_bp)
        app.register_blueprint(auth.auth_bp)

        db.create_all()

        return app
