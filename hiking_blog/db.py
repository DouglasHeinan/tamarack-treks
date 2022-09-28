from flask_sqlalchemy import SQLAlchemy

db = None


def instantiate_db(app):
    global db
    db = SQLAlchemy()
    db.init_app(app)


def create_db():
    db.create_all()
