"""This file is a collection of site maintenance operations accessible to a site administrator."""

from flask import Blueprint, flash, redirect, render_template, url_for, send_from_directory, request
from flask_login import current_user, login_required
from hiking_blog.auth.auth import admin_only
from hiking_blog.forms import UsernameForm, AddTrailForm, AddNewTrailPhotoForm, GearForm, CommentForm
from hiking_blog.models import User, Trails, Gear, TrailPictures
from hiking_blog.contact import send_async_email, send_email, send_username_rejected_notification, EMAIL
from hiking_blog.db import db
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil
import os
import errno
import re
import html

ADMIN_DELETE_MESSAGE = "This comment has been deleted for inappropriate content."
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
DIR_START = "hiking_blog/admin/static/"
NO_TAGS = re.compile("<.*?>")
NO_CHARS = re.compile("[^a-zA-Z]")


admin_bp = Blueprint(
    "admin_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


# ----------------------------------------MAIN PAGES----------------------------------------
@admin_bp.route("/tamarack-treks/admin/dashboard")
@admin_only
@login_required
def admin_dashboard():
    """
    Creates the landing page for the admin after accessing the admin menu.

    After logging in as an admin, an 'Admin' option is available in the navbar. If selected, it will run this function
    and create the admin landing page where a site-runner has access to functions that will make changes to the app.
    """

    pics_by_day = os.listdir("hiking_blog/admin/static/submitted_trail_pics")
    new_users = unapproved_usernames()
    folder = "hiking_blog/admin/static/submitted_trail_pics"
    pics_by_day = delete_empty_directories(folder, pics_by_day)
    return render_template("admin_dashboard.html", user=current_user, pics_by_day=pics_by_day, new_users=new_users)


@admin_bp.route("/tamarack-treks/admin/add_admin", methods=["GET", "POST"])
@admin_only
@login_required
def add_admin():
    """
    Changes a user's 'is_admin' status in the database to True.

    Allows a user already logged-in as an admin to change another user's 'is_admin' status in the database to True,
    giving the newly appointed admin site-runner privileges.
    """

    form = UsernameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("That username does not exist. Please try again.")
            return redirect(url_for("auth_bp.login"))
        if user.is_admin:
            flash("User already has admin status")
            return redirect(url_for("admin_bp.add_admin"))
        user.is_admin = True
        db.session.commit()
        return redirect(url_for("admin_bp.admin_dashboard"))
    return render_template("add_admin_form_page.html",
                           form=form,
                           form_header="Add Admin",
                           form_sub_header="Enter the username of the user to be given admin status:",
                           form_action="admin_bp.add_admin")


@admin_bp.route("/tamarack-treks/admin/add_trail", methods=["GET", "POST"])
@admin_only
@login_required
def add_trail():
    """
    Allows a user with admin privileges to add a trail entry to the database.

    When the form is submitted, its info is entered into the trails table of the database and the user is redirected to
    the home page.
    """

    form = AddTrailForm()
    if form.validate_on_submit():
        new_hiking_trail = Trails()
        update_trail_entry(new_hiking_trail, form)
        new_hiking_trail.date_time_added = datetime.now()
        db.session.add(new_hiking_trail)
        db.session.commit()
        trail_id = new_hiking_trail.id
        return redirect(url_for("admin_bp.add_initial_trail_photos", trail_id=trail_id))
    return render_template("trail_form_page.html", form=form)


@admin_bp.route("/tamarack-treks/admin/edit_trail/<int:trail_id>", methods=["GET", "POST"])
@admin_only
def edit_trail(trail_id):
    """
    Allows a user with admin privileges to edit an existing trail entry in the database.

    When the form is submitted, its info is entered into the trails table of the database, overwriting the previous
    data for that entry. and the user is redirected to the home page. The function for adding new trails is found in
    the admin module.

    PARAMETERS
    ----------
    trail_id : int
        The primary key for the specified trail entry in the trails table of the database
    """

    trail = Trails.query.get(trail_id)
    form = populate_trail_form(trail)

    if form.validate_on_submit():
        update_trail_entry(trail, form)
        db.session.commit()
        return redirect(url_for("trail_bp.view_trail", db_id=trail_id))
    return render_template("edit_trail_form_page.html", form=form, trail_id=trail_id)


@admin_bp.route("/tamarack-treks/<int:trail_id>/add_initial_trail_pics", methods=["GET", "POST"])
@login_required
def add_initial_trail_photos(trail_id):
    """
    Creates three new files to store newly added trail images upon admin creation of a new trail entry.

    When an admin creates a new trail entry, that entry must be created with a minimum of three trail images for
    the carousel on that trail's page. This function creates three new files for these three new images. They are
    submitted to the admin for review as with all user submitted images.
    """

    form = AddNewTrailPhotoForm()
    if form.validate_on_submit():
        file_one = form.filename_one.data
        file_two = form.filename_two.data
        file_three = form.filename_three.data
        result, message = check_files(trail_id, file_one, file_two, file_three)
        flash(message)
        return result
    else:
        return render_template("add_initial_trail_photos.html", form=form, trail_id=trail_id)


@admin_bp.route("/tamarack-treks/admin/add_gear", methods=["GET", "POST"])
@admin_only
@login_required
def add_gear():
    """
    Allows a user with admin privileges to add a gear entry to the database.

    When the form is submitted, its info is entered into the gear table of the database and the user is redirected to
    the home page.
    """

    form = GearForm()
    if form.validate_on_submit():
        new_gear_description = Gear()
        update_gear_entry(new_gear_description, form)
        new_gear_description.date_time_added = datetime.now()
        db.session.add(new_gear_description)
        db.session.commit()
        gear_id = new_gear_description.id
        return redirect(url_for("gear_bp.view_gear", db_id=gear_id))
    return render_template("gear_form_page.html", form=form)


@admin_bp.route("/tamarack-treks/admin/edit_gear/<int:gear_id>", methods=["GET", "POST"])
@admin_only
def edit_gear(gear_id):
    """
    Allows a user with admin privileges to edit a gear entry in the database.

    When the form is submitted, its info is entered into the gear table of the database and the user is redirected to
    the home page. The function for adding new gear is found in the admin module.

    PARAMETERS
    ----------
    gear_id : int
        The primary key for the specified gear item in the gear table of the database
    """

    gear = Gear.query.get(gear_id)
    form = populate_gear_form(gear)

    if form.validate_on_submit():
        update_gear_entry(gear, form)
        db.session.commit()
        return redirect(url_for("gear_bp.view_gear", db_id=gear_id))
    return render_template("edit_gear_form_page.html", form=form, gear_id=gear_id)


@admin_bp.route("/tamarack-treks/admin/dead_links/")
@admin_only
def dead_links():
    """
    Checks if any Gear database entries contain dead links and alerts the admin.

    Cycles through all entries in the gear table of the database, checking if any of the link_dead entries are True. If
    so, the name of the gear piece and its link are added to a list that is displayed on the admin dashboard.
    """

    all_gear = Gear.query.all()
    current_dead_links = []
    for gear in all_gear:
        if gear.moosejaw_link_dead:
            current_dead_links.append({gear.name: ["Moosejaw Link", gear.moosejaw_url]})
        if gear.rei_link_dead:
            current_dead_links.append({gear.name: ["REI Link", gear.rei_url]})
        if gear.backcountry_link_dead:
            current_dead_links.append({gear.name: ["Backcountry Link", gear.backcountry_url]})
    if not current_dead_links:
        print("No dead links.")
    return render_template("view_dead_links.html", links=current_dead_links)


@admin_bp.route("/tamarack-treks/admin/mark_out_of_stock/<gear_name>")
@admin_only
def mark_out_of_stock(gear_name):
    """
    Changes several entries in the database for a gear item that is out of stock at one of the linked retailers.

    When an admin determines that a link is dead because the item is out of stock with that retailer, this function
    changes several entries for that gear piece in the database: the link is to that retailer is no longer considered
    dead, so the data_scraper program will continue checking for updates to its status; the out_of_stock column becomes
    True; the price changes to "Out of Stock" to make it clear to the user why it isn't currently linked.
    """
    site = request.args["site"]
    gear_piece = Gear.query.filter_by(name=gear_name).first()
    if site == "Moosejaw Link":
        gear_piece.moosejaw_out_of_stock = True
        gear_piece.moosejaw_link_dead = False
        gear_piece.moosejaw_price = "Out of stock"
    if site == "REI Link":
        gear_piece.rei_out_of_stock = True
        gear_piece.rei_link_dead = False
        gear_piece.rei_price = "Out of stock"
    if site == "Backcountry Link":
        gear_piece.backcountry_out_of_stock = True
        gear_piece.backcountry_link_dead = False
        gear_piece.backcountry_price = "Out of stock"
    db.session.commit()
    return redirect(url_for("admin_bp.dead_links"))


# ----------------------------------------TRAIL PHOTO FUNCTIONS----------------------------------------
@admin_bp.route("/tamarack-treks/admin/submitted_trail_pics/<date>")
@login_required
@admin_only
def submitted_trail_pics(date):
    """
    Creates a dictionary of submitted but unapproved photo submissions from users.

    This function gathers all the currently unexamined photo submissions from users and puts them in a dictionary to be
    easily displayed in the template.

    PARAMETERS
    ----------
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    """

    photos = {}
    user_trail_directories = os.listdir(f"hiking_blog/admin/static/submitted_trail_pics/{date}")
    for directory in user_trail_directories:
        photos[str(directory)] = os.listdir(f"hiking_blog/admin/static/submitted_trail_pics/{date}/{directory}")
    is_empty = True
    for key in photos:
        if photos[key]:
            is_empty = False
    return render_template(
        "submitted_trail_pics.html",
        user_trail_directories=user_trail_directories,
        photos=photos, date=date, is_empty=is_empty
    )


@admin_bp.route("/tamarack-treks/admin/approve_submitted_photo/<date>/<user_trail>/<photo>")
@login_required
@admin_only
def approve_submitted_trail_pic(date, user_trail, photo):
    """
    Saves user-submitted photos to the database and posts them to the app.

    When the admin approves a photo, it is added to the database and then moved to the 'approved' directory. The user
    is emailed a notification that their photo has been approved.

    PARAMETERS
    ----------
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    user_trail : str
        A string that combines the user's username and the relevant trail's trail name. This is the name of the file
        that stores the user's photos. It is contained inside the date file.
    photo : str
        The file name of the user submitted photo. Must use one of the ALLOWED_EXTENSIONS.
    """

    username = user_trail.split("^")[0]
    trail_name = user_trail.split("^")[1]
    user = User.query.filter_by(username=username).first()
    trail = Trails.query.filter_by(name=trail_name).first()
    add_new_trail_photo(user, trail, photo, date)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


@admin_bp.route("/tamarack-treks/admin/delete_submitted_photo/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def delete_submitted_photo(date, user_trail, pic):
    """
    Deletes a user-submitted photo from the database and notifies the user of the deletion.

    If a user-submitted photo is clearly and unequivocally in violation of the site's terms of use and, in the opinion
    of the admin, in extremely poor taste, the admin will delete the photo from the database. The function will
    automatically notify the user of the deletion and the reason for it.

    PARAMETERS
    ----------
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    user_trail : str
        A string that combines the user's username and the relevant trail's trail name. This is the name of the file
        that stores the user's photos. It is contained inside the date file.
    pic : str
        The file name of the user submitted photo. Must use one of the ALLOWED_EXTENSIONS.
    """
    # ADD REASON FOR DELETION
    # DELETE BUTTON SHOULD BE SELECT BTN
    # ALL OPTIONS SHOULD GIVE SAME RETURN
    # SELECTED OPTION SHOULD BE INCLUDED IN EMAIL
    to_delete = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    save_pic = False
    create_photo_notification_email(user_trail, save_pic)
    if os.path.exists(to_delete):
        os.remove(to_delete)
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


@admin_bp.route("/tamarack-treks/admin/save_for_appeal/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def save_for_appeal(date, user_trail, pic):
    """
    Move user-submitted photos to a holding file for deletion or appeal.

    If a user-submitted photo is rejected for any inoffensive reason, the photo file is moved to a holding folder
    where it will remain for up to thirty days before it is deleted. The reason for the thirty day hold is so the user
    in question can make an appeal to have their photo displayed on the app. Examples of inoffensive reasons are:
    photos that have nothing to do with the trail in question, photos of exceptionally poor quality, or photos that
    feature people instead of the trail or surroundings. Photos that are rejected for offensive reasons are handled
    by a separate function.

    PARAMETERS
    ----------
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    user_trail : str
        A string that combines the user's username and the relevant trail's trail name. This is the name of the file
        that stores the user's photos. It is contained inside the date file.
    pic : str
        The file name of the user submitted photo. Must use one of the ALLOWED_EXTENSIONS.
    """
    # -------------------ADD RADIO BUTTONS FOR REASON WHY-------------------------------
    save_pic = "temp"
    print("about to move file")
    move_file_and_email_user(user_trail, save_pic, date, pic)
    print("done moving file")
    return redirect(url_for("admin_bp.submitted_trail_pics", date=date))


@admin_bp.route("/tamarack-treks/admin/static/submitted_trail_pic/<date>/<user_trail>/<pic>")
@login_required
@admin_only
def static_submitted_trail_pic(date, user_trail, pic):
    """Displays submitted trail photo."""
    path = f"{date}/{user_trail}/{pic}"
    return send_from_directory("admin/static/submitted_trail_pics/", path)


# ----------------------------------------PHOTO-RELATED FUNCTIONS----------------------------------------
def move_file_and_email_user(user_trail, save_pic, date, pic):
    """Moves user-submitted photos to the appropriate directory and emails user of the photo's status."""
    create_photo_notification_email(user_trail, save_pic)
    origin = f"hiking_blog/admin/static/submitted_trail_pics/{date}/{user_trail}/{pic}"
    if save_pic == "keep":
        sorting_directory = "approved"
    else:
        sorting_directory = "save_for_appeal_pics"
    target = create_file_name(sorting_directory, date, user_trail)
    shutil.move(origin, target)


def create_photo_notification_email(user_trail, save_pic):
    """Creates and sends the email that notifies the user of a change in their photo's status."""
    username = user_trail.split("^")[0]
    user = User.query.filter_by(username=username).first()
    user_email = user.email
    if save_pic == "temp":
        subject = "Your trail photo might have a problem"
        message = "The administrators have flagged your photo for some reason. Your photo will be kept for thirty " \
                  "days until it is removed from our servers. If you believe your photo has been flagged in error, " \
                  "please contact us through our contact page with the subject 'photo error' in the next thirty days " \
                  "and we will work with you to resolve the issue."
    elif save_pic == "keep":
        subject = "Your trail photo has been posted!"
        message = "Your photo has been approved by the admin and is now posted on the app."
    else:
        subject = "Your trail photo has been rejected."
        message = "The administrators have determined that your photo is inappropriate for this site and it has been " \
                  "deleted from the server."
    send_async_email(user_email, subject, message, send_email)


def check_files(trail_id, file_one, file_two, file_three):
    """
    Checks several file names for validity.

    Called by the add_initial_trail_pics function, check_files makes sure the user has actually input an image file
    before allowing new folders for those files to be stored in to be created.

    PARAMETERS
    ----------
    trail_id : int
        The database id number of an entry in the trails table.
    file_one, file_two, file_three : file
        The names of image files input by the user
    """

    message = None
    if file_one.filename == "" or file_two.filename == "" or file_three.filename == "":
        message = "No file selected."
        result = redirect(url_for("admin_bp.add_initial_trail_pics", trail_id=trail_id))
    elif allowed_file(file_one.filename) and allowed_file(file_two.filename) and allowed_file(file_three.filename):
        directory = create_initial_trail_directory(trail_id)
        create_initial_trail_pic_files(directory, file_one, file_two, file_three)
        photos = [file_one, file_two, file_three]
        approve_initial_trail_photos(trail_id, photos)
        result = redirect(url_for("trail_bp.view_trail", db_id=trail_id))
    else:
        message = "Invalid file type."
        result = redirect(url_for("admin_bp.add_initial_trail_pic", trail_id=trail_id))
    return result, message


def approve_initial_trail_photos(trail_id, photos):
    user = User.query.get(current_user.id)
    trail = Trails.query.get(trail_id)
    date = datetime.today().strftime("%m-%d-%Y")
    for photo in photos:
        add_new_trail_photo(user, trail, photo.filename, date)


# ----------------------------------------FILE AND DIRECTORY SORTING FUNCTIONS----------------------------------------
def create_initial_trail_directory(trail_id):
    """Creates a directory to store user-submitted photo files in."""
    date = datetime.today().strftime("%m-%d-%Y")
    user = User.query.get(current_user.id).username
    trail = Trails.query.get(trail_id).name
    user_trail = user + "^" + trail
    sorting_dir = "submitted_trail_pics/"
    directory = create_file_name(sorting_dir, date, user_trail)
    admin_upload_notification(EMAIL, user, trail)
    return directory


def create_initial_trail_pic_files(directory, file_one, file_two, file_three):
    """
    Creates and names three new files.

    This function is called by the add_initial_trail_pics function. It creates three new files and names them based on
    the name of the user, the id of the trail, and the current date. It also saves an image file in said folder.

    PARAMETERS
    ----------
    directory : str
        A directory folder name created by another function using the current date, the user's name, and a trail name.
    file_one, file_two, file_three : file
        The names of image files input by the user
    """

    filename_one = secure_filename(file_one.filename)
    file_one.save(os.path.join(directory, filename_one))
    filename_two = secure_filename(file_two.filename)
    file_two.save(os.path.join(directory, filename_two))
    filename_three = secure_filename(file_three.filename)
    file_three.save(os.path.join(directory, filename_three))


def make_new_directory(parent_dir, user_trail):
    """Creates a new directory if one with the appropriate name does not exist."""
    directory = f"{user_trail}"
    path = os.path.join(parent_dir, directory)
    os.makedirs(path)
    return path


def create_file_name(sorting_dir, date, user_trail):
    """
    Creates a new file for storing user-submitted photos.

    If the user has already submitted photos for the same trail on the same date, no new file will be created and the
    new submissions will be sent to the same directory as the others. Otherwise, a new directory will be created to
    store the photos.

    PARAMETERS
    ----------
    sorting_dir : str
        Names the directory (either 'submitted_trail_pics' or 'save_for_appeal_pics') that the submitted photo's date
        directory should be sent to.
    date : str
        The date, in string form, that the photos were submitted. The date of submission is also the name of the file
        created to store the file that stores their photos.
    user_trail : str
        A string that combines the user's username and the relevant trail's trail name. This is the name of the file
        that stores the user's photos. It is contained inside the date file.
    """

    parent_dir = f"{DIR_START}{sorting_dir}/{date}"
    directory = f"{parent_dir}/{user_trail}"
    in_existence = os.path.exists(directory)
    if not in_existence:
        directory = make_new_directory(parent_dir, user_trail)
    return directory


def delete_empty_directories(folder, directories):
    """
    Deletes empty user-submitted photo directories after their contents have been approved or rejected by an admin.

    This function is called upon loading the admin_dashboard function. Before rendering that template, this function
    iterates through the approved, save_for_appeal, and submitted_trail_pics directories in this blueprint's static
    folder. During that iteration, it iterates through each sub-directory, removing that sub-directory if it is empty.
    Then, it checks to see if the parent directory it's iterating through is empty, deleting it if it is. Finally, it
    returns a list of all directories that still have contents to be displayed in the admin_dashboard template.

    PARAMETERS
    ----------
    folder : str
        The pathway to be joined with each directory to be iterated through.
    directories : list
        A list of directories to be iterated through.
    """

    for directory in directories:
        working_directory = os.path.join(folder, directory)
        sub_directories = os.listdir(working_directory)
        for sub_directory in sub_directories:
            try:
                os.rmdir(os.path.join(working_directory, sub_directory))
            except OSError as e:
                if e.errno != errno.ENOTEMPTY:
                    raise
        try:
            os.rmdir(os.path.join(folder, directory))
        except OSError as e:
            if e.errno != errno.ENOTEMPTY:
                raise
    pics_by_day = os.listdir(folder)
    return pics_by_day


def allowed_file(filename):
    """Checks a user-submitted file to confirm it has one of the appropriate extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------------------------UTILITY FUNCTIONS----------------------------------------
def admin_upload_notification(email, user, trail):
    """Notifies the admin via email that a specific user has submitted a photo related to a specific trail."""
    subject = "User photo upload notification"
    message = f"User {user} has just uploaded photos for {trail} that need to be reviewed."
    send_async_email(email, subject, message, send_email)


def delete_comment(comment, db_id, page, admin_id):
    """
    Accessed from the view_gear and view_trail templates, deletes a comment specified by the admin.

    This function loads a comment form pre-populated with the contents of a comment the admin has deemed inappropriate.
    By submitting the form, the comment is deleted from the database and replaced with a message indicating that the
    comment was removed for being inappropriate.

    PARAMETERS
    ----------
    comment : obj
        The comment object targeted for deletion.
    db_id : str
        The primary key of the gear or trail entry in the database.
    page : str
        A string of either 'gear' or 'trail' used to direct the admin back to the correct page after the function runs.
    admin_id: str
        The database id number of the admin making the deletion.
    """

    form = CommentForm(
        comment_text=comment.text
    )
    next_page = render_template("delete_comment_form_page.html", form=form, text_box="comment_text")
    if form.validate_on_submit():
        commenter = User.query.get(admin_id)
        comment.deleted_by = commenter.username
        db.session.commit()
        form.comment_text.data = ""
        next_page = redirect(url_for(f"{page}_bp.view_{page}", db_id=db_id))
    return next_page


def unapproved_usernames():
    """Adds all users with unapproved usernames to a list that is made available to the admin for approval."""
    all_users = db.session.query(User).all()
    new_users = []
    for user in all_users:
        if user.username_needs_verification:
            new_users.append(user)
    return new_users


@admin_bp.route("/tamarack-treks/admin/approve_username/<user_id>")
@login_required
@admin_only
def approve_username(user_id):
    """Changes a user's username status to approved."""
    user = User.query.get(user_id)
    user.username_approved = True
    user.username_needs_verification = False
    db.session.commit()
    return redirect(url_for("admin_bp.admin_dashboard"))


@admin_bp.route("/tamarack-treks/admin/reject_username/<user_id>")
@login_required
@admin_only
def reject_username(user_id):
    """Triggers a function that the user an email letting them know their submitted username has been rejected."""
    user = User.query.get(user_id)
    send_username_rejected_notification(user)
    user.username_needs_verification = False
    db.session.commit()
    return redirect(url_for("admin_bp.admin_dashboard"))


def add_new_trail_photo(user, trail, photo, date):
    new_pic = TrailPictures(
        community_rating="Be the first to rate this photo!",
        img_taker=user.first_name + "" + user.last_name,
        img=photo,
        poster_id=user.id,
        trail_id=trail.id,
        date_time_added=datetime.now()
    )
    db.session.add(new_pic)
    db.session.commit()
    save_pic = "keep"
    user_trail = f"{user.username}^{trail.name}"
    move_file_and_email_user(user_trail, save_pic, date, photo)


def update_gear_entry(gear, form):
    """Activated during the edit_gear and add_gear functions, assigns all values in the database."""
    description_text = re.sub(NO_TAGS, '', form.description.data)
    gear.name = form.name.data
    gear.category = form.category.data
    gear.msrp = form.msrp.data
    gear.weight = form.weight.data
    gear.dimensions = form.dimensions.data
    gear.img = form.img.data
    gear.rating = form.rating.data
    gear.description = html.unescape(description_text)
    gear.gear_trail = "Gear"
    gear.moosejaw_url = form.moosejaw_url.data
    gear.moosejaw_price = form.moosejaw_price.data
    gear.moosejaw_link_dead = False
    gear.moosejaw_out_of_stock = False
    gear.rei_url = form.rei_url.data
    gear.rei_price = form.rei_price.data
    gear.rei_link_dead = False
    gear.rei_out_of_stock = False
    gear.backcountry_url = form.backcountry_url.data
    gear.backcountry_price = form.backcountry_price.data
    gear.backcountry_link_dead = False
    gear.backcountry_out_of_stock = False
    gear.keywords = form.keywords.data


def update_trail_entry(trail, form):
    """Activated during the edit_trail and add_trail functions, assigns all values in the database."""
    description_text = re.sub(NO_TAGS, '', form.description.data)
    trail.name = form.name.data
    trail.description = html.unescape(description_text)
    trail.gear_trail = "Trail"
    trail.latitude = form.latitude.data
    trail.longitude = form.longitude.data
    trail.hiking_dist = form.hiking_distance.data
    trail.elev_change = form.elevation_change.data
    trail.difficulty = form.difficulty.data


def populate_gear_form(gear):
    """Activated during the edit_gear function, populates all fields of the form with data from the database."""
    gear_piece = GearForm(
        name=gear.name,
        category=gear.category,
        msrp=gear.msrp,
        weight=gear.weight,
        dimensions=gear.dimensions,
        img=gear.img,
        rating=gear.rating,
        description=gear.description,
        moosejaw_url=gear.moosejaw_url,
        moosejaw_price=gear.moosejaw_price,
        rei_url=gear.rei_url,
        rei_price=gear.rei_price,
        backcountry_url=gear.backcountry_url,
        backcountry_price=gear.backcountry_price
    )
    return gear_piece


def populate_trail_form(trail):
    """Activated during the edit_trail function, populates all fields of the form with data from the database."""
    trail_to_edit = AddTrailForm(
        name=trail.name,
        description=trail.description,
        latitude=trail.latitude,
        longitude=trail.longitude,
        hiking_distance=trail.hiking_dist,
        elevation_change=trail.elev_change
    )
    return trail_to_edit
