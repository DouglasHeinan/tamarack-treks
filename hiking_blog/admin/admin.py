"""This file is a collection of admin site maintenance operations."""

from flask import Blueprint, flash, redirect, render_template, url_for, request, send_from_directory
from flask_login import current_user
from hiking_blog.auth.auth import admin_only
from hiking_blog.forms import AddAdminForm, AddTrailForm, GearForm, CommentForm
from hiking_blog.models import User, Trails, Gear, TrailPictures
from hiking_blog.contact import send_async_email
from hiking_blog.db import db
from flask_login import login_required
import shutil
import os

ADMIN_DELETE_MESSAGE = "This comment has been deleted for inappropriate content."
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
        new_review_gear = Gear()
        update_gear_entry(new_review_gear, form)
        db.session.add(new_review_gear)
        db.session.commit()
        return redirect(url_for("home_bp.home"))
    return render_template("add_gear.html", form=form)


@admin_bp.route("/admin/edit_gear/<int:gear_id>", methods=["GET", "POST"])
@admin_only
def edit_gear(gear_id):
    """
    Allows a user with admin privileges to edit a gear entry in the database.

    When the form is submitted, its info is entered into the gear table of the database and the user is redirected to
    the home page. The function for adding new gear is found in the admin module.

    Parameters
    ----------
    gear_id : int
        The primary key for the specified gear item in the gear table of the database
    """

    gear = Gear.query.get(gear_id)
    form = populate_gear_form(gear)

    if form.validate_on_submit():
        update_gear_entry(gear, form)
        db.session.commit()
        return redirect(url_for("gear_bp.view_gear", db_id=gear_id))
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


@admin_bp.route("/admin/static/submitted_trail_pic/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def static_submitted_trail_pic(date, user_trail, pic):
    path = f"{date}/{user_trail}/{pic}"
    return send_from_directory("admin/static/submitted_trail_pics/", path)


@admin_bp.route("/admin/approve_submitted_photo/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def approve_submitted_trail_pic(date, user_trail, pic):
    username = user_trail.split("^")[0]
    trail_name = user_trail.split("^")[1]
    user = User.query.filter_by(username=username).first()
    trail = Trails.query.filter_by(name=trail_name).first()
    new_pic = TrailPictures(
        img=pic,
        poster_id=user.id,
        trail_id=trail.id
    )
    db.session.add(new_pic)
    db.session.commit()
    to_delete = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    os.remove(to_delete)
    save_pic = "keep"
    create_photo_notification_email(user_trail, save_pic)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


@admin_bp.route("/admin/delete_submitted_photo/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def delete_submitted_photo(date, user_trail, pic):
    """
    Deletes a user-submitted photo from the database and notifies the user of the deletion.

    If a user-submitted photo is clearly and unequivocally in violation of the site's terms of use and, in the opinion
    of the admin, in extremely poor taste, the admin will delete the photo from the database. The function will
    automatically notify the user of the deletion and the reason for it.
    """
    to_delete = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    save_pic = False
    create_photo_notification_email(user_trail, save_pic)
    if os.path.exists(to_delete):
        os.remove(to_delete)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


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

    save_pic = "temp"
    create_photo_notification_email(user_trail, save_pic)
    origin = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    sorting_dir = "save_for_appeal_pics/"
    directory = create_file_name(sorting_dir, date, user_trail)
    target = directory
    shutil.move(origin, target)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


def create_photo_notification_email(user_trail, save_pic):
    username = user_trail.split("^")[0]
    user = User.query.filter_by(username=username).first()
    user_email = user.email
    if save_pic == "temp":
        subject = "Your trail photo has been rejected."
        message = "The administrators have determined that your photo is inappropriate for this site and it has been " \
                  "deleted from the server."
    elif save_pic == "keep":
        subject = "Your trail photo has been posted!"
        message = "Your photo has been approved by the admin and is now posted on the app."
    else:
        subject = "Your trail photo might have a problem"
        message = "The administrators have flagged your photo for some reason. Your photo will be  kept for thirty " \
                  "days until it is removed from our servers. If you believe your photo has been flagged in error, " \
                  "please contact us through our contact page with the subject 'photo error' in the next thirty days " \
                  "and we will work with you to resolve the issue."
    print(f"user = {username}, email = {user_email}.")
    send_async_email(user_email, subject, message)


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


def delete_comment(comment, db_id, page):
    """
    Accessed from the view_gear and view_trail templates, deletes a comment specified by the admin.

    This function loads a comment form pre-populated with the contents of a comment the admin has deemed inappropriate.
    By submitting the form, the comment is deleted from the database and replaced with a message indicating that the
    comment was removed for being inappropriate.

    Parameters
    ----------
    comment : obj
        The comment object targeted for deletion.
    db_id : str
        The primary key of the gear or trail entry in the database.
    page : str
        A string of either 'gear' or 'trail' used to direct the admin back to the correct page after the function runs.

    """

    form = CommentForm(
        comment_text=comment.text
    )
    next_page = render_template("edit_comment.html", form=form)
    if form.validate_on_submit():
        comment.text = ADMIN_DELETE_MESSAGE
        db.session.commit()
        form.comment_text.data = ""
        next_page = redirect(url_for(f"{page}_bp.view_{page}", db_id=db_id))
    return next_page


def update_gear_entry(gear, form):
    """Activated during the edit_gear and add_gear functions, assigns all values in the database."""
    gear.name = form.name.data
    gear.category = form.category.data
    gear.img_url = form.img_url.data
    gear.rating = form.rating.data
    gear.review = form.review.data
    gear.moosejaw_url = form.moosejaw_url.data
    gear.moosejaw_price = form.moosejaw_price.data
    gear.rei_url = form.rei_url.data
    gear.rei_price = form.rei_price.data
    gear.backcountry_url = form.backcountry_url.data
    gear.backcountry_price = form.backcountry_price.data


def populate_gear_form(gear):
    """Activated during the edit_gear function, populates all fields of the form with data from the database."""
    gear_piece = GearForm(
        name=gear.name,
        category=gear.category,
        img_url=gear.img_url,
        rating=gear.rating,
        review=gear.review,
        moosejaw_url=gear.moosejaw_url,
        moosejaw_price=gear.moosejaw_price,
        rei_url=gear.rei_url,
        rei_price=gear.rei_price,
        backcountry_url=gear.backcountry_url,
        backcountry_price=gear.backcountry_price
    )
    return gear_piece