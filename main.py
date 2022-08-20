from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired, URL
from wtforms import StringField, SubmitField, SelectField
from datetime import date
import smtplib


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
ckeditor = CKEditor(app)
Bootstrap(app)

EMAIL = os.environ["EMAIL"]
EMAIL_PW = os.environ["EMAIL_PW"]

GEAR_CATEGORIES = ["Tents", "Sleeping Bags", "Hiking Poles"]

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///outdoors.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


def main():

    class Trails(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        description = db.Column(db.Text, nullable=False)
        img_url = db.Column(db.String(250), nullable=False)
        latitude = db.Column(db.String(100), nullable=False)
        longitude = db.Column(db.String(100), nullable=False)
        hiking_dist = db.Column(db.Float, nullable=False)
        elev_change = db.Column(db.Integer, nullable=False)

    class Gear(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        category = db.Column(db.String(100), nullable=False)
        img_url = db.Column(db.String(250), unique=True, nullable=False)
        rating = db.Column(db.Float, nullable=False)
        review = db.Column(db.Text, nullable=False)

    class AddTrailForm(FlaskForm):
        name = StringField("Trail Name", validators=[DataRequired()])
        description = CKEditorField("Description", validators=[DataRequired()])
        latitude = StringField("Latitude", validators=[DataRequired()])
        longitude = StringField("Longitude", validators=[DataRequired()])
        img = StringField("Image URL", validators=[DataRequired(), URL()])
        hiking_distance = StringField("Hiking Distance in Miles", validators=[DataRequired()])
        elevation_change = StringField("Elevation Change", validators=[DataRequired()])
        submit_button = SubmitField("Submit")

    class ContactForm(FlaskForm):
        name = StringField("Name", validators=[DataRequired()])
        email = StringField("Email", validators=[DataRequired()])
        subject = StringField("Subject", validators=[DataRequired()])
        message = CKEditorField("Message", validators=[DataRequired()])
        submit_button = SubmitField("Submit")

    class GearForm(FlaskForm):
        name = StringField("Name of Piece", validators=[DataRequired()])
        category = SelectField("Gear Category", choices=GEAR_CATEGORIES, validators=[DataRequired()])
        img_url = StringField("Image URL", validators=[DataRequired()])
        rating = StringField("Gear Rating", validators=[DataRequired()])
        review = CKEditorField("Review", validators=[DataRequired()])
        submit_button = SubmitField("Submit")

    db.create_all()

    @app.route("/")
    def home():
        saved_trails = db.session.query(Trails).all()
        saved_gear = db.session.query(Gear).all()
        return render_template("index.html", all_trails=saved_trails, all_gear=saved_gear)

    @app.route("/add_trail", methods=["GET", "POST"])
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

    @app.route("/view_trail/<int:trail_id>")
    def view_trail(trail_id):
        requested_trail = Trails.query.get(trail_id)
        return render_template("view_trail.html", trail=requested_trail)

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

    @app.route("/view_gear/<int:gear_id>")
    def view_gear(gear_id):
        requested_gear = Gear.query.get(gear_id)
        return render_template("view_gear.html", gear=requested_gear)

    @app.context_processor
    def copyright_year():
        return dict(year=date.today().year)  # Copyright footer variable

    app.run(debug=True)


if __name__ == "__main__":
    main()
