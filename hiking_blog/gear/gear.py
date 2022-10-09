"""Contains the functionality for viewing gear info and creating gear entries in the database."""
from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user
from hiking_blog.forms import CommentForm, GearForm
from hiking_blog.models import Gear, GearComments
from hiking_blog.auth.auth import admin_only
from hiking_blog.db import db

gear_bp = Blueprint(
    "gear_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@gear_bp.route("/add_gear", methods=["GET", "POST"])
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


@gear_bp.route("/edit_gear/<int:gear_id>", methods=["GET", "POST"])
@admin_only
def edit_gear(gear_id):
    """
    Allows a user with admin privileges to edit a gear entry in the database.

    When the form is submitted, its info is entered into the gear table of the database and the user is redirected to
    the home page.
    """

    gear = Gear.query.get(gear_id)
    form = GearForm()

    form.name.data = gear.name
    form.category.data = gear.category
    form.img_url.data = gear.img_url
    form.rating.data = gear.rating
    form.review.data = gear.review
    form.moosejaw_url.data = gear.moosejaw_url
    form.moosejaw_price.data = gear.moosejaw_price
    form.rei_url.data = gear.rei_url
    form.rei_price.data = gear.rei_price
    form.backcountry_url.data = gear.backcountry_url
    form.backcountry_price.data = gear.backcountry_price

    if form.validate_on_submit():
        for field, value in form.data.items():
            if value is not None:
                gear.field = value
        db.session.commit()
        return redirect(url_for("home_bp.home"))
    return render_template("add_gear.html", form=form)


@gear_bp.route("/view_gear/<int:gear_id>", methods=["GET", "POST"])
def view_gear(gear_id):
    """
    Allows the user to view the information about a specific gear item stored in the gear table of the database.

    Directs the user to a template containing all stored information regarding a specific gear item in the database.
    Additionally, loads the comment form, allowing the user to comment on the gear and, when submitted, stores their
    comment in the database as well.

    Parameters
    ----------
    gear_id : int
        The primary key for the specified gear item in the gear table of the database
    """

    form = CommentForm()
    requested_gear = Gear.query.get(gear_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("auth_bp.login"))
        new_comment = GearComments(
            text=form.comment_text.data,
            commenter=current_user,
            parent_gear_posts=requested_gear
        )
        db.session.add(new_comment)
        db.session.commit()
        form.comment_text.data = ""
    return render_template("view_gear.html", gear=requested_gear, form=form, current_user=current_user)


@gear_bp.route("/view_prices/<gear_id>")
def view_prices(gear_id):
    """
    Renders a page of links to the specified piece of gear's Amazon, REI, and Backcountry pages.

    Scrapes the gear price from the three major retailers and creates a dictionary of the gear items' prices and
    retailer links. That dictionary is sent to a template which, when rendered, displays the price from each of the
    major retailers for the gear item in question and allows the user to visit their pages.

    Parameters
    ----------
    gear_id : int
        The primary key for the specified gear item in the gear table of the database
    """

    gear = Gear.query.get(gear_id)

    info = {
        "moosejaw": {"price": gear.moosejaw_price,
                     "link": gear.moosejaw_url},
        "rei": {"price": gear.rei_price,
                "link": gear.rei_url},
        "backcountry": {"price": gear.backcountry_price,
                        "link": gear.backcountry_url}
    }
    return render_template("gear_info.html", gear=gear, info=info)
