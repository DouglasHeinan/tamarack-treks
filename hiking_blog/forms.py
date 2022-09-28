from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL, Length, Email
from wtforms import StringField, SubmitField, SelectField, PasswordField
from flask_ckeditor import CKEditorField

GEAR_CATEGORIES = ["Tents", "Sleeping Bags", "Hiking Poles"]


class SignUpForm(FlaskForm):

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50)])
    verify_password = PasswordField("Verify Password", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


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
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    rating = StringField("Gear Rating", validators=[DataRequired()])
    review = CKEditorField("Review", validators=[DataRequired()])
    amazon_url = StringField("Amazon Link", validators=[DataRequired(), URL()])
    rei_url = StringField("REI Link", validators=[DataRequired(), URL()])
    backcountry_url = StringField("Backcountry Link", validators=[DataRequired(), URL()])
    submit_button = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")
