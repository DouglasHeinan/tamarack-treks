"""This file is a collection of admin site maintenance operations."""

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
DIR_START = "hiking_blog/admin/static/"


admin_bp = Blueprint(
    "admin_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@admin_bp.route("/admin/dashboard")
@admin_only
@login_required
def admin_dashboard():
    """
    Creates the landing page for the admin after accessing the admin menu.

    After logging in as an admin, an 'Admin' option is available in the navbar. If selected, it will run this function
    and create the admin landing page where a site-runner has access to functions that will make changes to the app.
    """

    pics_by_day = os.listdir("hiking_blog/admin/static/submitted_trail_pics")
    return render_template("admin_dashboard.html", user=current_user, pics_by_day=pics_by_day)


@admin_bp.route("/admin/add_admin", methods=["GET", "POST"])
@admin_only
@login_required
def add_admin():
    """
    Changes a user's 'is_admin' status in the database to True.

    Allows a user already logged-in as an admin to change another user's 'is_admin' status in the database to True,
    giving the newly appointed admin site-runner privileges.
    """

    form = AddAdminForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("That username does not exist. Please try again.")
            return redirect(url_for("auth_bp.login"))
        user.is_admin = True
        db.session.commit()
        return redirect(url_for("admin_bp.admin_dashboard"))
    return render_template("add_admin.html", form=form)


@admin_bp.route("/admin/add_trail", methods=["GET", "POST"])
@admin_only
@login_required
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
@login_required
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
    """
    Creates a dictionary of submitted but unapproved photo submissions from users.

    This function gathers all the currently unexamined photo submissions from users and puts them in a dictionary to be
    easily displayed in the template

    Parameters
    ----------
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    """

    pics = {}
    user_trail_directories = os.listdir(f"hiking_blog/admin/static/submitted_trail_pics/{date}")
    for directory in user_trail_directories:
        pics[str(directory)] = os.listdir(f"hiking_blog/admin/static/submitted_trail_pics/{date}/{directory}")
    return render_template(
        "submitted_trail_pics.html", user_trail_directories=user_trail_directories, pics=pics, date=date
    )


@admin_bp.route("/admin/save_for_appeal/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def save_for_appeal(date, user_trail, pic):
    """
    Move user-submitted photos to a holding file for deletion or appeal.

    If a user-submitted photo is rejected for any inoffensive reason, the photo file is moved to a holding folder
    where it will remain for up to thirty days before it is deleted. The reason for the thirty day hold is so the user
    in question can make an appeal to have their photo displayed on the app. Examples of inoffensive reasons are:
    photos that have nothing to do with the trail in question, photos of exceptionally poor quality, or photos that
    feature people instead of the trail or surroundings. Photos that are rejected for offensive reasons are handled
    by a separate function.

    Parameters
    ----------
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    user_trail : str
        A string that combines the user's username and the relevant trail's trail name. This is the name of the file
        that stores the user's photos. It is contained inside the date file.
    pic : str
        The file name of the user submitted photo. Must use one of the ALLOWED_EXTENSIONS.
    """

    origin = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    sorting_dir = "save_for_appeal_pics/"
    directory = create_file_name(sorting_dir, date, user_trail)
    target = directory
    shutil.move(origin, target)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


def make_new_directory(parent_dir, user_trail):
    """Creates a new directory if one with the appropriate name does not exist."""
    directory = f"{user_trail}"
    path = os.path.join(parent_dir, directory)
    os.makedirs(path)
    return path


def create_file_name(sorting_dir, date, user_trail):
    """
    Creates a new file for storing user-submitted photos.

    If the user has already submitted photos for the same trail on the same date, no new file will be created and the
    new submissions will be sent to the same directory as the others. Otherwise, a new directory will be created to
    store the photos.

    Parameters
    ----------
    sorting_dir : str
        Names the directory (either 'submitted_trail_pics' or 'save_for_appeal_pics') that the submitted photo's date
        directory should be sent to.
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    user_trail : str
        A string that combines the user's username and the relevant trail's trail name. This is the name of the file
        that stores the user's photos. It is contained inside the date file.
    """

    parent_dir = f"{DIR_START}{sorting_dir}{date}"
    directory = f"{parent_dir}/{user_trail}"
    in_existence = os.path.exists(directory)
    if not in_existence:
        directory = make_new_directory(parent_dir, user_trail)
    return directory


def allowed_file(filename):
    """Checks a user-submitted file to confirm it has one of the appropriate extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
