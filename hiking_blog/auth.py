from flask import Blueprint, render_template, redirect, flash, request, url_for, abort
from hiking_blog.forms import SignUpForm, LoginForm
from flask_login import login_required, logout_user, current_user, login_user
from hiking_blog.models import User
from functools import wraps
from hiking_blog.login_manager import login_manager
from datetime import timedelta
from hiking_blog.db import db


DAYS_BEFORE_LOGOUT = timedelta(days=30)


auth_bp = Blueprint(
    "auth_bp", __name__
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("That username does not exist. Please try again.")
            return redirect(url_for("auth_bp.login"))
        if not user.check_password(password=form.password.data):
            flash("Password incorrect. Please Try again.")
            return redirect(url_for("auth_bp.login"))
        login_user(user, remember=True, duration=DAYS_BEFORE_LOGOUT)
        print("user logged in?" + str(current_user.is_authenticated))
        next_page = request.args.get("next")
        return redirect(next_page or url_for("home_bp.home"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@auth_bp.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("You've already signed up!")
            return redirect(url_for("auth_bp.login"))
        if form.password.data != form.verify_password.data:
            flash("Passwords Must Match")
            return redirect(url_for("auth_bp.sign_up"))
        new_user = User(
            username=form.username.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home_bp.home"))
    return render_template("sign_up.html", form=form, logged_in=current_user.is_authenticated)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_bp.home"))


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page")
    return redirect(url_for("auth_bp.login"))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
