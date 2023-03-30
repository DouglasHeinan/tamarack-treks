"""Creates the home blueprint and runs the home and about routes."""
from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from flask_login import current_user
from hiking_blog.models import Trails, Gear
from hiking_blog.db import db
# This import only exists for development purposes
from hiking_blog.dev_db_autofill import create_database

WELCOME_TEXT = "Tamarack Treks is an online resource and community that aims to help you explore Western Montana in" \
               " the best way possible. Discover new local trails or explore some hidden gems in a new mountain range." \
               " Search for a new campsite - free, paid, car-camping or backpacking - and read campsite reviews." \
               " Explore gear reviews focused on gear tested during all four seasons in Western Montana. Western" \
               " Montana is situated in the northern Rocky Mountains where a number of unique ranges, rivers, and" \
               " habitats create a beautiful, wild outdoor space. The hiking, camping and outdoor recreational" \
               " opportunities are limitless. We will help you explore it all."

home_bp = Blueprint(
    "home_bp",
    __name__,
    template_folder="templates",
    static_folder="static"
)


@home_bp.route("/tamarack-treks")
def home():
    """
    Renders the home page.

    Loads all information on saved trails and gear from the database to be sent to the dashboard.html template before
    rendering said template.
    """

    saved_trails = db.session.query(Trails).all()
    saved_gear = db.session.query(Gear).all()
    # The create_database function only exists for development purposes.
    if not saved_gear:
        create_database()
        return redirect(url_for("home_bp.home"))
    # End of development only code.
    recent_trails = db.session.query(Trails).order_by(Trails.date_time_added)[:-4:-1]
    recent_gear = db.session.query(Gear).order_by(Gear.date_time_added)[:-4:-1]
    return render_template(
        "dashboard.html",
        all_trails=saved_trails,
        all_gear=saved_gear,
        recent_trails=recent_trails,
        recent_gear=recent_gear,
        logged_in=current_user.is_authenticated,
        user=current_user,
        body_text=WELCOME_TEXT
    )


@home_bp.route("/home/static/dev_pics/<file_name>")
def display_main_carousel_pics(file_name):
    """Displays the carousel pictures on the home page."""
    return send_from_directory("home/static/dev_pics/", file_name)


@home_bp.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html")
