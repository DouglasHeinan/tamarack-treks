from flask import Blueprint, flash, redirect, render_template, url_for, send_from_directory
from flask_login import current_user
from hiking_blog.auth.auth import admin_only
from hiking_blog.forms import AddAdminForm, AddTrailForm, GearForm
from hiking_blog.models import User, Trails, Gear
from hiking_blog.db import db
from flask_login import login_required
import os


admin_bp = Blueprint(
    "admin_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@admin_bp.route("/admin_dashboard")
@admin_only
def admin_dashboard():
    return render_template("admin_dashboard.html", user=current_user)


@admin_bp.route("/add_admin", methods=["GET", "POST"])
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


@admin_bp.route("/add_trail", methods=["GET", "POST"])
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


@admin_bp.route("/add_gear", methods=["GET", "POST"])
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


@admin_bp.route("/submitted_trail_pics")
@admin_only
def submitted_trail_pics():
    all_pics = os.listdir("hiking_blog/static/submitted_trail_pics/")
    return render_template("submitted_trail_pics.html", all_pics=all_pics)


@admin_bp.route("/admin/submitted_trail_pics/static/<path>")
@login_required
@admin_only
def static_submitted_trail_pic(path):
    return send_from_directory("admin/static/submitted_trail_pics", path)
