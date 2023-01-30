from flask import Blueprint, request, redirect, render_template, url_for
from hiking_blog.models import User, Gear, Trails, Favorites
from hiking_blog.db import db


user_profile_bp = Blueprint(
    "user_profile_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@user_profile_bp.route("/user_profile/<user_id>")
def user_profile_dashboard(user_id):
    user = User.query.get(user_id)
    return render_template("user_profile.html", user=user)


@user_profile_bp.route("/user_profile/<user_id>/comments")
def user_profile_comments(user_id):
    user = User.query.get(user_id)
    return render_template("user_comments.html", user=user)


@user_profile_bp.route("/user_profile/<user_id>/view_photos")
def view_submitted_photos(user_id):
    user = User.query.get(user_id)
    return render_template("view_submitted_photos.html", user=user)


@user_profile_bp.route("/user_profile/<user_id>/favorite_trail")
def add_favorite(user_id):
    user = User.query.get(user_id)
    gear_trail = request.args["gear_trail"]
    favorite_id = request.args["favorite_id"]
    if gear_trail == "Gear":
        favorite = Gear.query.get(favorite_id)
    else:
        favorite = Trails.query.get(favorite_id)
    create_new_favorite(favorite, user_id)
    return redirect(url_for('user_profile_bp.user_profile_dashboard', user_id=user.id))


@user_profile_bp.route("/user_profile/<user_id>/view_favorites")
def view_favorites(user_id):
    user = User.query.get(user_id)
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    return render_template("user_profile_favorites.html", favorites=favorites, user=user)


def create_new_favorite(favorite, user_id):
    new_favorite = Favorites(
        name=favorite.name,
        gear_trail=favorite.gear_trail,
        description=favorite.description,
        user_id=user_id
    )
    if favorite.gear_trail == "Gear":
        new_favorite.img = favorite.img
    else:
        new_favorite.img = favorite.trail_page_pics[0].img
    db.session.add(new_favorite)
    db.session.commit()
