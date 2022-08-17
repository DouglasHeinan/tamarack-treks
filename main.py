from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired, URL
from wtforms import StringField, SubmitField
from datetime import date


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
ckeditor = CKEditor(app)
Bootstrap(app)

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

    class AddTrailForm(FlaskForm):
        name = StringField("Trail Name", validators=[DataRequired()])
        description = CKEditorField("Description", validators=[DataRequired()])
        latitude = StringField("Latitude", validators=[DataRequired()])
        longitude = StringField("Longitude", validators=[DataRequired()])
        img = StringField("Image URL", validators=[DataRequired(), URL()])
        hiking_distance = StringField("Hiking Distance in Miles", validators=[DataRequired()])
        elevation_change = StringField("Elevation Change", validators=[DataRequired()])
        submit_button = SubmitField("Submit")

    db.create_all()

    @app.route("/")
    def home():
        saved_trails = db.session.query(Trails).all()
        return render_template("index.html", all_trails=saved_trails)

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

    @app.context_processor
    def copyright_year():
        return dict(year=date.today().year)  # Copyright footer variable

    app.run(debug=True)


if __name__ == "__main__":
    main()
