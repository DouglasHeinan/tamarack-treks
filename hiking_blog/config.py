import os


class Config:
    # config variables
    FLASK_ENV = "development"
    TESTING = True
    SECRET_KEY = "fdjkls;a"
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///hiking_db.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

#     RESET ENVIRON VARIABLES!!!!!!!!
