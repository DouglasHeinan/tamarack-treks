"""Contains the functionality for viewing trail info and creating trail entries in the database."""
from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
from hiking_blog.forms import CommentForm, AddTrailPicForm
from hiking_blog.models import Trails, TrailComments, db, User
from werkzeug.utils import secure_filename
from hiking_blog.admin.admin import make_new_directory, allowed_file
from hiking_blog.auth.auth import admin_only
from datetime import datetime
import os

DIR_START = "hiking_blog/admin/static/submitted_trail_pics/"

PICTURE_UPLOAD_SUCCESS = "You're photos have been successfully uploaded! They will now need to be vetted by one " \
                         "of our administrators. This process usually only takes a day or two. Once you're photo " \
                         "has been approved, you will be notified via email. Thank you for supporting the blah-blah " \
                         "community!"

trail_bp = Blueprint(
    "trail_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@trail_bp.route("/<int:trail_id>/view_trail", methods=["GET", "POST"])
def view_trail(trail_id):
    """
    Allows the user to view the information  about a specific trail stored in the trails table of the database.

    Directs the user to a template containing all stored information regarding a specific trail in the database.
    Additionally, loads the comment form, allowing the user to comment on the trail and, when submitted, stores their
    comment in the database as well.

    Parameters
    ----------
    trail_id : int
        The primary key for the specified trail in the trails table of the database
    """
    form = CommentForm()
    requested_trail = Trails.query.get(trail_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("auth_bp.login"))
        new_comment = TrailComments(
            text=form.comment_text.data,
            commenter=current_user,
            parent_trail_posts=requested_trail
        )
        db.session.add(new_comment)
        db.session.commit()
        form.comment_text.data = ""
    return render_template("view_trail.html", trail=requested_trail, form=form, current_user=current_user)


@trail_bp.route("/<int:trail_id>/add_trail_pic", methods=["GET", "POST"])
@login_required
def add_trail_pic(trail_id):
    form = AddTrailPicForm()
    if form.validate_on_submit():
        file = form.filename.data
        if file.filename == "":
            flash("No file selected.")
            return redirect(url_for("trail_bp.add_trail_pic", trail_id=trail_id))
        if allowed_file(file.filename):
            user = User.query.get(current_user.id).username
            trail = Trails.query.get(trail_id).name
            user_trail = user + "^" + trail
            date = datetime.today().strftime("%m-%d-%Y")
            parent_dir = f"{DIR_START}{date}"
            directory = f"{parent_dir}/{user_trail}"
            in_existence = os.path.exists(directory)
            if not in_existence:
                directory = make_new_directory(parent_dir, user_trail)
            filename = secure_filename(file.filename)
            file.save(os.path.join(directory, filename))
            flash(PICTURE_UPLOAD_SUCCESS)
            # admin should receive email here
            return redirect(url_for("trail_bp.view_trail", trail_id=trail_id))
        else:
            flash("Invalid file type.")
            return redirect(url_for("trail_bp.add_trail_pic", trail_id=trail_id))
    return render_template("add_trail_pics.html", form=form)

