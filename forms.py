from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL, Length
from wtforms import StringField, SubmitField, SelectField, PasswordField
from flask_ckeditor import CKEditorField

GEAR_CATEGORIES = ["Tents", "Sleeping Bags", "Hiking Poles"]


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50)])
    submit_button = SubmitField("Submit")


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


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")