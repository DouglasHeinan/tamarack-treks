from flask import Flask
from hiking_blog import db
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from hiking_blog import login_manager


def init_app():
    ckeditor = CKEditor()
    bootstrap = Bootstrap()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    login_manager.create_login_manager(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    with app.app_context():
        db.instantiate_db(app)

        from hiking_blog.home import dashboard
        from hiking_blog.gear import gear
        from hiking_blog.trails import trails
        from hiking_blog import contact, auth

        app.register_blueprint(dashboard.home_bp)
        app.register_blueprint(gear.gear_bp)
        app.register_blueprint(trails.trail_bp)
        app.register_blueprint(contact.contact_bp)
        app.register_blueprint(auth.auth_bp)

        db.create_db()

        return app


if __name__ == "__main__":
    app = init_app()
    app.run(debug=True)
