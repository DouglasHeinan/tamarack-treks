"""The collection of form classes used in this application."""

from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, URL, Length, Email
from wtforms import StringField, SelectField, PasswordField

GEAR_CATEGORIES = ["Tents", "Sleeping Bags", "Trekking Poles", "Furniture", "Kitchen"]


class SignUpForm(FlaskForm):
    """
    A class used for the applications sign-up form.

    When submitted, the provided information is added to the database in the user table.
    """

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(message="Please enter a valid email address.")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50)])
    verify_password = PasswordField("Verify Password", validators=[DataRequired()])


class LoginForm(FlaskForm):
    """
    A class used for the application's login form.

    When submitted, the provided information is compared against information in the database to log the user in.
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50)])


class UsernameRecoveryForm(FlaskForm):
    """A class used for reminding a user of their username."""
    email = StringField("Email", validators=[DataRequired(), Email()])


class UsernameForm(FlaskForm):
    """A class used for creating a form that resets a username, recovers a password, or add an admin."""
    username = StringField("Username", validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    """A class used for creating a password reset form."""
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8, max=50)])
    verify_password = PasswordField("Verify Password", validators=[DataRequired()])


class AddTrailForm(FlaskForm):
    """
    A class used for the application's add_trail form, accessible only if the user is admin.

    When submitted, the information provided will be added to the trails table of the database.
    """

    name = StringField("Trail Name", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    latitude = StringField("Latitude", validators=[DataRequired()])
    longitude = StringField("Longitude", validators=[DataRequired()])
    hiking_distance = StringField("Hiking Distance", validators=[DataRequired()])
    elevation_change = StringField("Elev Change", validators=[DataRequired()])
    difficulty = SelectField("Difficulty", choices=["Easy", "Medium", "Hard"], validators=[DataRequired()])


class AddTrailPhotoForm(FlaskForm):
    """A class for a form that submits a new image file."""
    filename = FileField("File", validators=[FileRequired()])


class AddNewTrailPhotoForm(FlaskForm):
    """A class for a form that submits a three new image files."""
    filename_one = FileField("File", validators=[FileRequired()])
    filename_two = FileField("File", validators=[FileRequired()])
    filename_three = FileField("File", validators=[FileRequired()])


class ContactForm(FlaskForm):
    """A class used for the application's contact form."""
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(message="Please enter a valid email address.")])
    subject = StringField("Subject", validators=[DataRequired()])
    message = CKEditorField("Message", validators=[DataRequired()])


class GearForm(FlaskForm):
    """
    A class used for the application's gear form, accessible only if the user is admin.

    When submitted, the information provided will be added to the gear table of the database.
    """

    name = StringField("Name", validators=[DataRequired()])
    category = SelectField("Category", choices=GEAR_CATEGORIES, validators=[DataRequired()])
    msrp = StringField("MSRP", validators=[DataRequired()])
    weight = StringField("Weight", validators=[DataRequired()])
    dimensions = StringField("Dimensions", validators=[DataRequired()])
    img = StringField("Image URL", validators=[DataRequired(), URL()])
    rating = StringField("Gear Rating", validators=[DataRequired()])
    description = CKEditorField("Review", validators=[DataRequired()])
    moosejaw_url = StringField("MJ Link", validators=[])
    moosejaw_price = StringField("MJ Price", validators=[])
    rei_url = StringField("REI Link", validators=[])
    rei_price = StringField("REI Price", validators=[])
    backcountry_url = StringField("BC Link", validators=[])
    backcountry_price = StringField("BC Price", validators=[])
    keywords = StringField("Keywords", validators=[])


class CommentForm(FlaskForm):
    """A class used for the application's comment form."""
    comment_text = CKEditorField("Comment", validators=[DataRequired()])


class SearchForm(FlaskForm):
    """A class used for the applications search form."""
    searched = StringField("Search", validators=[DataRequired()])
