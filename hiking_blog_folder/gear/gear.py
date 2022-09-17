from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user
from ..forms import CommentForm, GearForm
from ..models import Gear, GearComments, db
from ..auth import admin_only

gear_bp = Blueprint(
    "gear_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@gear_bp.route("/add_gear", methods=["GET", "POST"])
@admin_only
def add_gear():
    form = GearForm()
    if form.validate_on_submit():
        new_review_gear = Gear(
            name=form.name.data,
            category=form.category.data,
            img_url =form.img_url.data,
            rating=form.rating.data,
            review=form.review.data
        )
        db.session.add(new_review_gear)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_gear.html", form=form)


@gear_bp.route("/view_gear/<int:gear_id>", methods=["GET", "POST"])
def view_gear(gear_id):
    form = CommentForm()
    requested_gear = Gear.query.get(gear_id)
    print("user view_gear logged in?" + str(current_user.is_authenticated))
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("login"))
        new_comment = GearComments(
            text=form.comment_text.data,
            commenter=current_user,
            parent_gear_posts=requested_gear
        )
        db.session.add(new_comment)
        db.session.commit()
        form.comment_text.data = ""
    return render_template("view_gear.html", gear=requested_gear, form=form, current_user=current_user)
