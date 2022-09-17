from flask import Blueprint, render_template
from flask_login import current_user
from ..models import db, Trails, Gear
from datetime import date


home_bp = Blueprint(
    "home_bp",
    __name__,
    template_folder="templates",
    static_folder="static"
)


@home_bp.route("/")
def home():
    saved_trails = db.session.query(Trails).all()
    saved_gear = db.session.query(Gear).all()
    print("home user logged in = " + str(current_user.is_authenticated))
    return render_template("dashboard.html", all_trails=saved_trails, all_gear=saved_gear,
                           logged_in=current_user.is_authenticated)


@home_bp.route("/about")
def about():
    return render_template("about.html")


@home_bp.context_processor
def copyright_year():
    return dict(year=date.today().year)  # Footer copyright variable
