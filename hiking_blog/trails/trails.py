"""Contains the functionality for viewing trail info and creating trail entries in the database."""
from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user
from hiking_blog.forms import CommentForm, AddTrailForm
from hiking_blog.models import Trails, TrailComments, db
from hiking_blog.auth.auth import admin_only

trail_bp = Blueprint(
    "trail_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@trail_bp.route("/view_trail/<int:trail_id>", methods=["GET", "POST"])
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
