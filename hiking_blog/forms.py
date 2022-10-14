"""The collection of form classes used in this application."""

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL, Length, Email
from wtforms import StringField, SubmitField, SelectField, PasswordField
from flask_ckeditor import CKEditorField

GEAR_CATEGORIES = ["Tents", "Sleeping Bags", "Hiking Poles"]


class SignUpForm(FlaskForm):
    """
    A class used for the applications sign-up form.

    When submitted, the provided information is added to the database in the user table.
    """

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50)])
    verify_password = PasswordField("Verify Password", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class LoginForm(FlaskForm):
    """
    A class used for the application's login form.

    When submitted, the provided information is compared against information in the database to log the user in.
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50)])
    submit_button = SubmitField("Submit")


class PasswordRecoveryForm(FlaskForm):
    """A class used for creating a password recovery form."""
    username = StringField("Username", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class VerificationForm(FlaskForm):
    """A class used for creating a password verification form."""
    verification_code = StringField("Verification Code", validators=[DataRequired(), Length(min=8, max=8)])
    submit_button = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    """A class used for creating a password reset form."""
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8, max=50)])
    verify_password = PasswordField("New Password", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class AddAdminForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class AddTrailForm(FlaskForm):
    """
    A class used for the application's add_trail form, accessible only if the user is admin.

    When submitted, the information provided will be added to the trails table of the database.
    """

    name = StringField("Trail Name", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    latitude = StringField("Latitude", validators=[DataRequired()])
    longitude = StringField("Longitude", validators=[DataRequired()])
    hiking_distance = StringField("Hiking Distance in Miles", validators=[DataRequired()])
    elevation_change = StringField("Elevation Change", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class ContactForm(FlaskForm):
    """A class used for the application's contact form."""

    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = CKEditorField("Message", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class GearForm(FlaskForm):
    """
    A class used for the application's gear form, accessible only if the user is admin.

    When submitted, the information provided will be added to the gear table of the database.
    """

    name = StringField("Name of Piece", validators=[DataRequired()])
    category = SelectField("Gear Category", choices=GEAR_CATEGORIES, validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    rating = StringField("Gear Rating", validators=[DataRequired()])
    review = CKEditorField("Review", validators=[DataRequired()])
    moosejaw_url = StringField("Moosejaw Link", validators=[DataRequired(), URL()])
    moosejaw_price = StringField("Moosejaw Price", validators=[DataRequired()])
    rei_url = StringField("REI Link", validators=[DataRequired(), URL()])
    rei_price = StringField("REI Price", validators=[DataRequired()])
    backcountry_url = StringField("Backcountry Link", validators=[DataRequired(), URL()])
    backcountry_price = StringField("Backcountry Price", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class CommentForm(FlaskForm):
    """A class used for the application's comment form."""

    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")
