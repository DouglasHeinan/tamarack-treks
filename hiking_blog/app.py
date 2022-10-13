"""Sets configurations and runs the app."""
from flask import Flask
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from hiking_blog import login_manager, db, mail
from datetime import date
from flask_executor import Executor


def init_app():
    """
    Initialises and runs the app.

    Configures the app using the config file, registers the flask blueprints from each of the packages, creates the
    database, and runs the app.
    """

    ckeditor = CKEditor()
    bootstrap = Bootstrap()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    executor = Executor(app)
    mail.create_mail(app)
    login_manager.create_login_manager(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    @app.context_processor
    def copyright_year():
        """Keeps footer copyright date current on every page of the app."""
        return dict(year=date.today().year)

    with app.app_context():
        db.init_db(app)

        from hiking_blog.home import dashboard
        from hiking_blog.gear import gear
        from hiking_blog.trails import trails
        from hiking_blog.auth import auth
        from hiking_blog import contact

        app.register_blueprint(dashboard.home_bp)
        app.register_blueprint(gear.gear_bp)
        app.register_blueprint(trails.trail_bp)
        app.register_blueprint(contact.contact_bp)
        app.register_blueprint(auth.auth_bp)

        db.create_db()
        #
        # thread1 = Thread(target=gear_prices.update_gear_prices)
        # thread1.daemon = True
        # thread1.start()
        # data_scraper.async_update_gear_info(gear_prices.update_gear_prices)
        # executor.submit(gear_prices.update_gear_prices)
        return app


if __name__ == "__main__":
    app = init_app()
    app.run(debug=True)
