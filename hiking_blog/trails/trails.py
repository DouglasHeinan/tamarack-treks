"""Contains the functionality for viewing trail info and creating trail entries in the database."""
from flask import render_template, redirect, url_for, flash, Blueprint, request, send_from_directory
from flask_login import current_user, login_required
from hiking_blog.forms import CommentForm, AddTrailPhotoForm
from hiking_blog.models import Trails, TrailComments, RatedPhoto, db
from hiking_blog.admin.admin import allowed_file, create_initial_trail_directory, delete_comment, NO_TAGS
from hiking_blog.auth.auth import admin_only
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re
import html

PICTURE_UPLOAD_SUCCESS = "You're photos have been successfully uploaded! They will now need to be vetted by one " \
                         "of our administrators. This process usually only takes a day or two. Once you're photo " \
                         "has been approved, you will be notified via email. Thank you for supporting the Tamarack " \
                         "Treks community!"

trail_bp = Blueprint(
    "trail_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@trail_bp.route("/gear/view_all_trails")
def view_all_trails():
    """Collects all trail items from the database to display to the user."""
    all_trails = db.session.query(Trails).all()
    return render_template("view_all_trails.html", all_trails=all_trails)


@trail_bp.route("/<int:db_id>/view_trail", methods=["GET", "POST"])
def view_trail(db_id):
    """
    Allows the user to view the information  about a specific trail stored in the trails table of the database.

    Directs the user to a template containing all stored information regarding a specific trail in the database.
    Additionally, loads the comment form, allowing the user to comment on the trail and, when submitted, stores their
    comment in the database as well.

    PARAMETERS
    ----------
    db_id : int
        The primary key for the specified trail in the trails table of the database
    """
    form = CommentForm()
    trail = Trails.query.get(db_id)
    # trail_pics = TrailPictures.query.filter_by(trail_id=db_id).all()
    # pic_ids = [pic.id for pic in trail_pics]
    if current_user.is_authenticated:
        user_rated_pics = RatedPhoto.query.filter_by(user_id=current_user.id).all()
        user_rated_pic_ids = [pic.photo_id for pic in user_rated_pics]
    else: user_rated_pic_ids = []
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("auth_bp.login"))
        create_new_trail_comment(form, trail)
        form.comment_text.data = ""
        return redirect(url_for('trail_bp.view_trail', db_id=db_id))
    return render_template("view_trail.html", trail=trail, form=form, current_user=current_user, user_rated_pic_ids=user_rated_pic_ids)


@trail_bp.route("/trail/edit_comment/<comment_id>", methods=["GET", "POST"])
def edit_trail_comment(comment_id):
    """Allows a user to edit one of their own comments on a piece of gear from the database."""
    db_id = request.args["trail_id"]
    comment = TrailComments.query.get(comment_id)
    form = CommentForm(
        comment_text=comment.text
    )
    if form.validate_on_submit():
        comment.text = re.sub(NO_TAGS, '', form.comment_text.data)
        db.session.commit()
        form.comment_text.data = ""
        return redirect(url_for("trail_bp.view_trail", db_id=db_id))
    return render_template("edit_trail_comment_form_page.html",
                           form=form,
                           comment_id=comment_id,
                           db_id=db_id,
                           text_box="comment_text")


@trail_bp.route("/trail/delete_comment/<comment_id>")
def user_delete_trail_comment(comment_id):
    """Allows a user to delete one of their own comments on a piece of gear from the database."""
    trail_id = request.args["trail_id"]
    comment = TrailComments.query.get(comment_id)
    comment.deleted_by = comment.commenter.username
    db.session.commit()
    return redirect(url_for("trail_bp.view_trail", db_id=trail_id))


@trail_bp.route("/trail/admin_delete/<comment_id>", methods=["GET", "POST"])
@admin_only
def admin_delete_trail_comment(comment_id):
    """Allows a user with admin privileges to delete a gear comment from the database."""
    admin_id = request.args["admin_id"]
    trail_id = request.args["trail_id"]
    comment = TrailComments.query.get(comment_id)
    next_page = delete_comment(comment, trail_id, "trail", admin_id)
    return next_page


@trail_bp.route("/<int:trail_id>/add_trail_pic", methods=["GET", "POST"])
@login_required
def add_trail_photo(trail_id):
    """Adds a new trail picture to the database."""
    form = AddTrailPhotoForm()
    if form.validate_on_submit():
        message, result = check_file(form, trail_id)
        flash(message)
        return result
    return render_template("add_trail_photo_form_page.html", form=form, trail_id=trail_id)


@trail_bp.route("/trails/static/dev_pics/<file_name>")
def display_trail_pics(file_name):
    """Displays trail pics to the user."""
    return send_from_directory("trails/static/dev_pics/", file_name)


def create_new_trail_comment(form, trail):
    """Creates a new entry in the trail_comments table of the database."""
    comment_text = re.sub(NO_TAGS, '', form.comment_text.data)
    new_comment = TrailComments(
        text=html.unescape(comment_text),
        deleted_by=None,
        date_time_added=datetime.now(),
        commenter=current_user,
        parent_posts=trail
    )
    db.session.add(new_comment)
    db.session.commit()


# --------------------------------SHOULD BE COMBINED WITH ADMIN CHECK FILES FUNCTION---------------------------------
def check_file(form, trail_id):
    """Checks that the user has submitted a valid file before creating a new directory to store that file."""

    file = form.filename.data
    if file.filename == "":
        message = "No file selected."
        result = redirect(url_for("trail_bp.add_trail_pic", trail_id=trail_id))
    elif allowed_file(file.filename):
        directory = create_initial_trail_directory(trail_id)
        filename = secure_filename(file.filename)
        file.save(os.path.join(directory, filename))
        message = PICTURE_UPLOAD_SUCCESS
        result = redirect(url_for("trail_bp.view_trail", db_id=trail_id, modal=True))
    else:
        message = "Invalid file type."
        result = redirect(url_for("trail_bp.add_trail_pic", trail_id=trail_id))
    return message, result
