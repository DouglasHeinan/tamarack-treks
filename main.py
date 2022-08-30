from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy.orm import relationship
from datetime import date
import smtplib
from forms import LoginForm, AddTrailForm, CommentForm, GearForm, ContactForm
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
ckeditor = CKEditor(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///outdoors.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

EMAIL = os.environ["EMAIL"]
EMAIL_PW = os.environ["EMAIL_PW"]


def main():

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def admin_only(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.id != 1:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function

    class User(UserMixin, db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(25), unique=True, nullable=False)
        password = db.Column(db.String(25), nullable=False)
        trail_page_comments = relationship("TrailComments", back_populates="commenter")
        gear_page_comments = relationship("GearComments", back_populates="commenter")

    class Trails(db.Model):
        __tablename__ = "trails"
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        description = db.Column(db.Text, nullable=False)
        img_url = db.Column(db.String(250), nullable=False)
        latitude = db.Column(db.String(100), nullable=False)
        longitude = db.Column(db.String(100), nullable=False)
        hiking_dist = db.Column(db.Float, nullable=False)
        elev_change = db.Column(db.Integer, nullable=False)
        comments = relationship("TrailComments", back_populates="parent_trail_posts")

    class Gear(db.Model):
        __tablename__ = "gear_rev"
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        category = db.Column(db.String(100), nullable=False)
        img_url = db.Column(db.String(250), unique=True, nullable=False)
        rating = db.Column(db.Float, nullable=False)
        review = db.Column(db.Text, nullable=False)
        comments = relationship("GearComments", back_populates="parent_gear_posts")

    class TrailComments(UserMixin, db.Model):
        __tablename__ = "trail_comments"
        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.Text, nullable=False)
        commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
        commenter = relationship("User", back_populates="trail_page_comments")
        trail_id = db.Column(db.Integer, db.ForeignKey("trails.id"))
        parent_trail_posts = relationship("Trails", back_populates="comments")

    class GearComments(UserMixin, db.Model):
        __tablename__ = "gear_comments"
        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.Text, nullable=False)
        commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
        commenter = relationship("User", back_populates="gear_page_comments")
        gear_id = db.Column(db.Integer, db.ForeignKey("gear_rev.id"))
        parent_gear_posts = relationship("Gear", back_populates="comments")

    db.create_all()

    @app.route("/")
    def home():
        saved_trails = db.session.query(Trails).all()
        saved_gear = db.session.query(Gear).all()
        return render_template("index.html", all_trails=saved_trails, all_gear=saved_gear,
                               logged_in=current_user.is_authenticated)

    @app.route("/sign_up", methods=["GET", "POST"])
    def sign_up():
        form = LoginForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("You've already signed up!")
                return redirect(url_for("login"))
            hashed_pw = generate_password_hash(
                form.password.data,
                method="pbkdf2:sha256",
                salt_length=8
            )
            new_user = User(
                username=form.username.data,
                password=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
        return render_template("sign_up.html", form=form, logged_in=current_user.is_authenticated)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if not user:
                flash("That username does not exist. Please try again.")
                return redirect(url_for("login"))
            if not check_password_hash(user.password, password):
                flash("Password incorrect. Please Try again.")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("home"))
        return render_template("login.html", form=form, logged_in=current_user.is_authenticated)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))

    @app.route("/add_trail", methods=["GET", "POST"])
    @admin_only
    def new_trail():
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

    @app.route("/view_trail/<int:trail_id>", methods=["GET", "POST"])
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

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            name = form.name.data,
            email = form.email.data,
            subject = form.subject.data,
            message = form.message.data

            with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                connection.starttls()
                connection.login(user=EMAIL, password=EMAIL_PW)
                connection.sendmail(
                    from_addr=EMAIL,
                    to_addrs=EMAIL,
                    msg=f"Subject: {subject}\n\nSent by:{name}, {email}\n{message}"
                )
            return redirect(url_for("home"))
        return render_template("contact.html", form=form)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/new_gear_review", methods=["GET", "POST"])
    @admin_only
    def new_gear_review():
        form = GearForm()
        if form.validate_on_submit():
            new_gear_review = Gear(
            name=form.name.data,
            category=form.category.data,
            img_url =form.img_url.data,
            rating=form.rating.data,
            review=form.review.data
            )
            db.session.add(new_gear_review)
            db.session.commit()
            return redirect(url_for("home"))
        return render_template("new_gear_review.html", form=form)

    @app.route("/view_gear/<int:gear_id>", methods=["GET", "POST"])
    def view_gear(gear_id):
        form = CommentForm()
        requested_gear = Gear.query.get(gear_id)
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

    @app.context_processor
    def copyright_year():
        return dict(year=date.today().year)  # Footer copyright variable

    app.run(debug=True)


if __name__ == "__main__":
    main()
