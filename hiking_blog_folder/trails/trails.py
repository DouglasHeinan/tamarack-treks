from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user
from ..forms import CommentForm, AddTrailForm
from ..models import Trails, TrailComments, db
from ..auth import admin_only

trail_bp = Blueprint(
    "trail_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@trail_bp.route("/add_trail", methods=["GET", "POST"])
@admin_only
def add_trail():
    form = AddTrailForm()
    if form.validate_on_submit():
        new_hiking_trail = Trails(
            name=form.name.data,
            description=form.description.data,
            img_url=form.img.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            hiking_dist=form.hiking_distance.data,
            elev_change=form.elevation_change.data
        )
        db.session.add(new_hiking_trail)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_trail.html", form=form)


@trail_bp.route("/view_trail/<int:trail_id>", methods=["GET", "POST"])
def view_trail(trail_id):
    form = CommentForm()
    requested_trail = Trails.query.get(trail_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("login"))
        new_comment = TrailComments(
            text=form.comment_text.data,
            commenter=current_user,
            parent_trail_posts=requested_trail
        )
        db.session.add(new_comment)
        db.session.commit()
        form.comment_text.data = ""
    return render_template("view_trail.html", trail=requested_trail, form=form, current_user=current_user)
