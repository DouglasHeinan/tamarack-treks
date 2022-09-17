from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    trail_page_comments = relationship("TrailComments", back_populates="commenter")
    gear_page_comments = relationship("GearComments", back_populates="commenter")

    def set_password(self, password):
        self.password = generate_password_hash(
            password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Trails(db.Model):
    __tablename__ = "trails"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    hiking_dist = db.Column(db.Float, nullable=False)
    elev_change = db.Column(db.Integer, nullable=False)
    comments = relationship("TrailComments", back_populates="parent_trail_posts")


class Gear(db.Model):
    __tablename__ = "gear_rev"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String(250), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text, nullable=False)
    comments = relationship("GearComments", back_populates="parent_gear_posts")


class TrailComments(UserMixin, db.Model):
    __tablename__ = "trail_comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commenter = relationship("User", back_populates="trail_page_comments")
    trail_id = db.Column(db.Integer, db.ForeignKey("trails.id"))
    parent_trail_posts = relationship("Trails", back_populates="comments")


class GearComments(UserMixin, db.Model):
    __tablename__ = "gear_comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commenter = relationship("User", back_populates="gear_page_comments")
    gear_id = db.Column(db.Integer, db.ForeignKey("gear_rev.id"))
    parent_gear_posts = relationship("Gear", back_populates="comments")

