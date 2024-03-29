"""Contains the functionality for viewing gear info and editing gear entries in the database."""
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_login import current_user
from hiking_blog.admin.admin import delete_comment, NO_TAGS
from hiking_blog.forms import CommentForm
from hiking_blog.models import Gear, GearComments
from hiking_blog.auth.auth import admin_only
from hiking_blog.db import db
from datetime import datetime
import re
import html

gear_bp = Blueprint(
    "gear_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@gear_bp.route("/tamarack-treks/gear/view_all_gear")
def view_all_gear():
    """Collects all gear items from the database to display to the user."""
    all_gear = db.session.query(Gear).all()
    return render_template("view_all_gear.html", all_gear=all_gear)


@gear_bp.route("/tamarack-treks/gear/view_gear/<int:db_id>", methods=["GET", "POST"])
def view_gear(db_id):
    """
    Allows the user to view the information about a specific gear item.

    Directs the user to a template containing all stored information regarding a gear item in the database.
    Additionally, loads the comment form, allowing the user to comment on the gear and, when submitted, stores their
    comment in the database as well.

    Parameters
    ----------
    db_id : int
        The primary key for the specified gear item in the gear table of the database
    """

    form = CommentForm()
    gear = Gear.query.get(db_id)
    info = create_product_links(gear)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("auth_bp.login"))
        create_new_gear_comment(form, gear)
        form.comment_text.data = ""
        return redirect(url_for('gear_bp.view_gear', db_id=db_id))
    return render_template("view_gear.html", gear=gear, form=form, current_user=current_user, info=info)


@gear_bp.route("/tamarack-treks/gear/edit_comment/<comment_id>", methods=["GET", "POST"])
def edit_gear_comment(comment_id):
    """Allows a user to edit one of their own comments on a piece of gear from the database."""
    db_id = request.args["gear_id"]
    comment = GearComments.query.get(comment_id)
    form = CommentForm(
        comment_text=comment.text
    )
    if form.validate_on_submit():
        comment.text = re.sub(NO_TAGS, '', form.comment_text.data)
        db.session.commit()
        form.comment_text.data = ""
        return redirect(url_for("gear_bp.view_gear", db_id=db_id))
    return render_template("edit_gear_comment_form_page.html",
                           form=form,
                           comment_id=comment_id,
                           db_id=db_id,
                           text_box="comment_text")


@gear_bp.route("/tamarack-treks/gear/delete_comment/<comment_id>")
def user_delete_gear_comment(comment_id):
    """
    Allows a user to delete one of their own comments on a piece of gear from the database.

    Any comment deleted by the user is still saved in the database. The text of the comment is replaced in the comments
    display with a message indicating that the user deleted their own comment.

    PARAMETERS
    ----------
    comment_id : int
        The id number of an entry in the comments table of the database.
    """

    gear_id = request.args["gear_id"]
    comment = GearComments.query.get(comment_id)
    comment.deleted_by = comment.commenter.username
    db.session.commit()
    return redirect(url_for("gear_bp.view_gear", db_id=gear_id))


@gear_bp.route("/tamarack-treks/gear/admin_delete/<comment_id>", methods=["GET", "POST"])
@admin_only
def admin_delete_gear_comment(comment_id):
    """
    Allows a user with admin privileges to delete a gear comment from the database.

    Any comment deleted by the admin is still saved in the database. The text of the comment is replaced in the
    comments display with a message indicating that the admin deleted the user's comment.

    PARAMETERS
    ----------
    comment_id : int
        The id number of an entry in the comments table of the database.
    """

    admin_id = request.args["admin_id"]
    gear_id = request.args["gear_id"]
    comment = GearComments.query.get(comment_id)
    next_page = delete_comment(comment, gear_id, "gear", admin_id)
    return next_page


def create_new_gear_comment(form, gear):
    """
    Creates a new comment entry in the GearComments table of the database.

    Parameters
    ----------
    form : object
        A form object with user-input data.
    gear : object
        An object from the gear table of the database.
    """

    comment_text = re.sub(NO_TAGS, '', form.comment_text.data)
    new_comment = GearComments(
        text=html.unescape(comment_text),
        deleted_by=None,
        date_time_added=datetime.now(),
        commenter=current_user,
        parent_posts=gear
    )
    db.session.add(new_comment)
    db.session.commit()


def create_product_links(gear):
    """
    Creates a python dictionary containing the price and url of a gear entry.

    This function is used by the view_gear function. It creates a dictionary that the view_gear.html page can cycle
    through to access the price and url for each link of each product.

    Parameters
    ----------
    gear : object
        An object from the gear table of the database.
    """

    info = {
        "moosejaw": {"price": gear.moosejaw_price,
                     "link": gear.moosejaw_url},
        "rei": {"price": gear.rei_price,
                "link": gear.rei_url},
        "backcountry": {"price": gear.backcountry_price,
                        "link": gear.backcountry_url}
    }
    return info
