from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired, URL
from wtforms import StringField, SubmitField




app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
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
        coordinates = db.Column(db.String(100), nullable=False)
        length = db.Column(db.Float, nullable=False)
        elev_change = db.Column(db.Integer, nullable=False)

    class AddTrailForm(FlaskForm):
        name = StringField("Trail Name", validators=[DataRequired()])
        description = StringField("Description", validators=[DataRequired()])
        lattitude = StringField("Lattitude", validators=[DataRequired()])
        longitude = StringField("Longitude", validators=[DataRequired()])
        img = StringField("Image URL", validators=[DataRequired(), URL()])
        length = StringField("Distance", validators=DataRequired())
        elevation = StringField("Elevation Change", validators=DataRequired())


    @app.route("/")
    def home():
        return render_template("index.html")

    app.run(debug=True)


if __name__ == "__main__":
    main()
