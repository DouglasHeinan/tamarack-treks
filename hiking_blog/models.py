"""The collection of database tables used in this application."""

from hiking_blog.db import db
from flask import current_app as app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    """A class used to represent a user."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False)
    trail_page_comments = relationship("TrailComments", back_populates="commenter")
    gear_page_comments = relationship("GearComments", back_populates="commenter")
    trail_page_pics = relationship("TrailPictures", back_populates="pic_poster")

    def set_password(self, password):
        """
        Generates a hashed password for the user.

        Parameters
        ----------
        password : str
            The password input by the user.
        """

        self.password = generate_password_hash(
            password,
            method="pbkdf2:sha256",
            salt_length=8
        )

    def check_password(self, password):
        """
        Compares the values from two password fields input by the user to confirm they match.

        Parameters
        ----------
        password : str
            The password input by the user.
        """

        return check_password_hash(self.password, password)

    def get_pw_reset_confirmation_token(self):
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="email-reset")
        return s.dumps(self.email, salt="email-reset")

    @staticmethod
    def verify_mail_confirmation_token(token):
        try:
            s = URLSafeTimedSerializer(
                app.config["SECRET_KEY"], salt="email-reset"
            )
            email = s.loads(token, salt="email-reset", max_age=3600)
            return email
        except (SignatureExpired, BadSignature):
            return None


class Trails(db.Model):
    """A class used to represent a trail information and review page."""
    __tablename__ = "trails"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    hiking_dist = db.Column(db.Float, nullable=False)
    elev_change = db.Column(db.Integer, nullable=False)
    trail_page_comments = relationship("TrailComments", back_populates="parent_trail_posts")
    trail_page_pics = relationship("TrailPictures", back_populates="parent_trail_posts")


class TrailPictures(db.Model):
    __tablename__ = "trail_pics"
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(250), unique=True, nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    pic_poster = relationship("User", back_populates="trail_page_pics")
    trail_id = db.Column(db.Integer, db.ForeignKey("trails.id"))
    parent_trail_posts = relationship("Trails", back_populates="trail_page_pics")


class TrailComments(UserMixin, db.Model):
    """A class used to represent the accumulated comments from the trail pages."""
    __tablename__ = "trail_comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commenter = relationship("User", back_populates="trail_page_comments")
    trail_id = db.Column(db.Integer, db.ForeignKey("trails.id"))
    parent_trail_posts = relationship("Trails", back_populates="trail_page_comments")


class Gear(db.Model):
    """A class used to represent a gear information and review page."""
    __tablename__ = "gear_rev"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String(250), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text, nullable=False)
    moosejaw_url = db.Column(db.String(250))
    moosejaw_price = db.Column(db.String(50))
    rei_url = db.Column(db.String(250))
    rei_price = db.Column(db.String(50))
    backcountry_url = db.Column(db.String(250))
    backcountry_price = db.Column(db.String(50))
    gear_comments = relationship("GearComments", back_populates="parent_gear_posts")


class GearComments(UserMixin, db.Model):
    """A class used to represent the accumulated comments from the gear pages."""
    __tablename__ = "gear_comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commenter = relationship("User", back_populates="gear_page_comments")
    gear_id = db.Column(db.Integer, db.ForeignKey("gear_rev.id"))
    parent_gear_posts = relationship("Gear", back_populates="gear_comments")
