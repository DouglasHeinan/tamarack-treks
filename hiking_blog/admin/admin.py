from flask import Blueprint, flash, redirect, render_template, url_for, send_from_directory
from flask_login import current_user
from hiking_blog.auth.auth import admin_only
from hiking_blog.forms import AddAdminForm, AddTrailForm, GearForm
from hiking_blog.models import User, Trails, Gear
from hiking_blog.db import db
from flask_login import login_required
import shutil
import os

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
DIR_START = "hiking_blog/admin/static/save_for_appeal_pics/"


admin_bp = Blueprint(
    "admin_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@admin_bp.route("/admin/dashboard")
@admin_only
def admin_dashboard():
    pics_by_day = os.listdir("hiking_blog/admin/static/submitted_trail_pics")
    return render_template("admin_dashboard.html", user=current_user, pics_by_day=pics_by_day)


@admin_bp.route("/admin/add_admin", methods=["GET", "POST"])
@admin_only
def add_admin():
    form = AddAdminForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("That username does not exist. Please try again.")
            return redirect(url_for("auth_bp.login"))
        user.is_admin = True
        db.session.commit()
        return redirect(url_for("home_bp.home"))
    return render_template("add_admin.html", form=form)


@admin_bp.route("/admin/add_trail", methods=["GET", "POST"])
@admin_only
def add_trail():
    """
    Allows a user with admin privileges to add a trail entry to the database.

    When the form is submitted, its info is entered into the trails table of the database and the user is redirected to
    the home page.
    """

    form = AddTrailForm()
    if form.validate_on_submit():
        new_hiking_trail = Trails(
            name=form.name.data,
            description=form.description.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            hiking_dist=form.hiking_distance.data,
            elev_change=form.elevation_change.data
        )
        db.session.add(new_hiking_trail)
        db.session.commit()
        return redirect(url_for("home_bp.home"))
    return render_template("add_trail.html", form=form)


@admin_bp.route("/admin/add_gear", methods=["GET", "POST"])
@admin_only
def add_gear():
    """
    Allows a user with admin privileges to add a gear entry to the database.

    When the form is submitted, its info is entered into the gear table of the database and the user is redirected to
    the home page.
    """

    form = GearForm()
    if form.validate_on_submit():
        new_review_gear = Gear(
            name=form.name.data,
            category=form.category.data,
            img_url =form.img_url.data,
            rating=form.rating.data,
            review=form.review.data,
            moosejaw_url=form.moosejaw_url.data,
            moosejaw_price=form.moosejaw_price.data,
            rei_url=form.rei_url.data,
            rei_price=form.rei_price.data,
            backcountry_url=form.backcountry_url.data,
            backcountry_price=form.backcountry_price.data
        )
        db.session.add(new_review_gear)
        db.session.commit()
        return redirect(url_for("home_bp.home"))
    return render_template("add_gear.html", form=form)


@admin_bp.route("/admin/submitted_trail_pics/<date>")
@login_required
@admin_only
def submitted_trail_pics(date):
    pics = {}
    user_trail_directories = os.listdir(f"hiking_blog/admin/static/submitted_trail_pics/{date}")
    for directory in user_trail_directories:
        pics[str(directory)] = os.listdir(f"hiking_blog/admin/static/submitted_trail_pics/{date}/{directory}")
    return render_template(
        "submitted_trail_pics.html", user_trail_directories=user_trail_directories, pics=pics, date=date
    )


@admin_bp.route("/admin/submitted_trail_pics/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def static_submitted_trail_pic(date, user_trail, pic):
    path = f"{date}/{user_trail}/{pic}"
    return send_from_directory("admin/static/submitted_trail_pics/", path)


@admin_bp.route("/admin/save_for_appeal/<date>/<user_trail>/<pic>")
def save_for_appeal(date, user_trail, pic):
    origin = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    parent_dir = f"{DIR_START}{date}"
    directory = f"{parent_dir}/{user_trail}"
    in_existence = os.path.exists(directory)
    if not in_existence:
        directory = make_new_directory(parent_dir, user_trail)
    target = directory
    shutil.move(origin, target)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


def make_new_directory(parent_dir, user_trail):
    directory = f"{user_trail}"
    path = os.path.join(parent_dir, directory)
    os.makedirs(path)
    return path


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS