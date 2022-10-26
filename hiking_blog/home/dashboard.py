"""Creates the home blueprint and runs the home and about routes."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from hiking_blog.models import Trails, Gear
from hiking_blog.db import db
# This import only exists for development purposes
from hiking_blog.dev_db_autofill import create_gear_reviews, create_trail_entries, create_users, create_trail_pic_entries

home_bp = Blueprint(
    "home_bp",
    __name__,
    template_folder="templates",
    static_folder="static"
)


@home_bp.route("/")
def home():
    """
    Renders the home page.

    Loads all information on saved trails and gear from the database to be sent to the dashboard.html template before
    rendering said template.
    """

    saved_trails = db.session.query(Trails).all()
    saved_gear = db.session.query(Gear).all()
    # This if statement only exists for development purposes.
    if not saved_gear:
        create_gear_reviews()
        create_trail_entries()
        create_users()
        create_trail_pic_entries()
        return redirect(url_for("home_bp.home"))
    return render_template("dashboard.html", all_trails=saved_trails, all_gear=saved_gear,
                           logged_in=current_user.is_authenticated, user=current_user)


@home_bp.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html")
