"""Contains the functionality for viewing trail info and creating trail entries in the database."""
from flask import render_template, redirect, url_for, flash, Blueprint, request, send_from_directory
from flask_login import current_user, login_required
from hiking_blog.forms import CommentForm, AddTrailPicForm
from hiking_blog.models import Trails, TrailComments, db, User
from hiking_blog.admin.admin import allowed_file, create_file_name, delete_comment
from hiking_blog.contact import send_async_email, send_email, EMAIL
from hiking_blog.auth.auth import admin_only
from werkzeug.utils import secure_filename
from datetime import datetime
import os


PICTURE_UPLOAD_SUCCESS = "You're photos have been successfully uploaded! They will now need to be vetted by one " \
                         "of our administrators. This process usually only takes a day or two. Once you're photo " \
                         "has been approved, you will be notified via email. Thank you for supporting the blah-blah " \
                         "community!"

trail_bp = Blueprint(
    "trail_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@trail_bp.route("/gear/view_all_trails")
def view_all_trails():
    all_trails = db.session.query(Trails).all()
    return render_template("view_all_trails.html", all_trails=all_trails)


@trail_bp.route("/<int:db_id>/view_trail", methods=["GET", "POST"])
def view_trail(db_id):
    """
    Allows the user to view the information  about a specific trail stored in the trails table of the database.

    Directs the user to a template containing all stored information regarding a specific trail in the database.
    Additionally, loads the comment form, allowing the user to comment on the trail and, when submitted, stores their
    comment in the database as well.

    Parameters
    ----------
    db_id : int
        The primary key for the specified trail in the trails table of the database
    """
    form = CommentForm()
    requested_trail = Trails.query.get(db_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("auth_bp.login"))
        new_comment = TrailComments(
            text=form.comment_text.data,
            deleted_by=None,
            commenter=current_user,
            parent_trail_posts=requested_trail
        )
        db.session.add(new_comment)
        db.session.commit()
        form.comment_text.data = ""
    return render_template("view_trail.html", trail=requested_trail, form=form, current_user=current_user)


@trail_bp.route("/trail/edit_comment/<comment_id>", methods=["GET", "POST"])
def edit_trail_comment(comment_id):
    """Allows a user to edit one of their own comments on a piece of gear from the database."""
    trail_id = request.args["trail_id"]
    comment = TrailComments.query.get(comment_id)
    form = CommentForm(
        comment_text=comment.text
    )
    if form.validate_on_submit():
        comment.text = form.comment_text.data
        db.session.commit()
        form.comment_text.data = ""
        return redirect(url_for("trail_bp.view_trail", db_id=trail_id))
    return render_template("form_page.html",
                           form=form,
                           h_two="Edit Comment",
                           p_tag="Edit your comment here.",
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
# Break this into smaller chunks
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
            sorting_dir = "submitted_trail_pics/"
            directory = create_file_name(sorting_dir, date, user_trail)
            filename = secure_filename(file.filename)
            file.save(os.path.join(directory, filename))
            flash(PICTURE_UPLOAD_SUCCESS)
            admin_upload_notification(EMAIL, user, trail)
            return redirect(url_for("trail_bp.view_trail", db_id=trail_id))
        else:
            flash("Invalid file type.")
            return redirect(url_for("trail_bp.add_trail_pic", trail_id=trail_id))
    return render_template("form_page.html",
                           form=form,
                           form_header="Add New Trail Pictures",
                           form_sub_header="Share some photos of this trail!")


@trail_bp.route("/trails/static/dev_pics/<file_name>")
def display_trail_pics(file_name):
    return send_from_directory("trails/static/dev_pics/", file_name)


def admin_upload_notification(email, user, trail):
    subject = "User photo upload notification"
    message = f"User {user} has just uploaded photos for {trail} that need to be reviewed."
    send_async_email(email, subject, message, send_email)
