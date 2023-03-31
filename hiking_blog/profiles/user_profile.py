from flask import Blueprint, request, redirect, render_template, url_for, flash
from hiking_blog.models import User, Gear, Trails, Favorites, RatedPhoto, TrailPictures
from hiking_blog.db import db
from datetime import datetime


user_profile_bp = Blueprint(
    "user_profile_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>")
def user_profile_dashboard(user_id):
    """Renders the user-profile dashboard"""
    user = User.query.get(user_id)
    recent_trail_favorites, recent_gear_favorites = get_recent_favorites(user.favorites)
    recent_rated_photos = get_recent_rated_photos(user.rated_pics)
    recent_submitted_photos = get_recent_submitted_photos(user.trail_page_pics)
    recent_trail_comments, recent_gear_comments = get_recent_comments(user.gear_page_comments, user.trail_page_comments)
    return render_template(
        "user_profile.html",
        user=user,
        recent_trail_favorites=recent_trail_favorites,
        recent_gear_favorites=recent_gear_favorites,
        recent_rated_photos=recent_rated_photos,
        recent_submitted_photos=recent_submitted_photos,
        recent_trail_comments=recent_trail_comments,
        recent_gear_comments=recent_gear_comments
    )


@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>/<sort_by>/view_comments")
def view_submitted_comments(user_id, sort_by):
    """Renders the user-profile submitted comments page, displaying all comments submitted by the user."""
    user = User.query.get(user_id)
    gear_comments = user.gear_page_comments
    trail_comments = user.trail_page_comments
    if sort_by == "date":
        date = True
    else:
        date = False
    ordered_gear_comments, ordered_trail_comments = get_ordered_comments(date, gear_comments, trail_comments)
    return render_template(
        "user_comments.html",
        user=user,
        gear_comments=ordered_gear_comments,
        trail_comments=ordered_trail_comments,
        date=date
    )


@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>/<sort_by>/view_photos")
def view_submitted_photos(user_id, sort_by):
    """Renders the user-profile submitted photos page, displaying all photos submitted by the user."""
    user = User.query.get(user_id)
    photos = user.trail_page_pics
    if sort_by == "date":
        date = True
    else:
        date = False
    ordered_photos = get_ordered_photos(date, photos)
    return render_template("view_submitted_photos.html", user=user, photos=ordered_photos, date=date)


@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>/rated_photos")
def view_rated_photos(user_id):
    """Renders the user-profile rated photos page, displaying all photos rated by the user with their ratings."""
    rated_photos = RatedPhoto.query.filter_by(user_id=user_id).all()
    one_photos, two_photos, three_photos, four_photos, five_photos = get_photo_ratings(rated_photos)
    user = User.query.get(user_id)
    return render_template(
        "user_profile_rated_pics.html",
        user=user,
        one_photos=one_photos,
        two_photos=two_photos,
        three_photos=three_photos,
        four_photos=four_photos,
        five_photos=five_photos
    )


@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>/<sort_by>/view_favorites")
def view_favorites(user_id, sort_by):
    """Renders the user-profile favorites page, displaying all database entries favorited by the user."""
    user = User.query.get(user_id)
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    gear_favorites = []
    trail_favorites = []
    for favorite in favorites:
        if favorite.gear_trail == "Gear":
            gear_favorites.append(favorite)
        else:
            trail_favorites.append(favorite)
    ordered_gear_favorites, ordered_trail_favorites = get_ordered_favorites(gear_favorites, trail_favorites, sort_by)
    return render_template(
        "user_profile_favorites.html",
        gear_favorites=ordered_gear_favorites,
        trail_favorites=ordered_trail_favorites,
        user=user
    )


# ----------------------------------DASHBOARD FUNCTIONS---------------------------------
def get_recent_favorites(user_favorites):
    user_favorites.sort(key=get_date_time_added)
    gear_favorites = []
    trail_favorites = []
    for favorite in user_favorites:
        if favorite.gear_trail == "Gear":
            new_favorite = Gear.query.filter_by(name=favorite.name).first()
            gear_favorites.append(new_favorite)
        else:
            new_favorite = Trails.query.filter_by(name=favorite.name).first()
            trail_favorites.append(new_favorite)
    recent_gear_favorites = gear_favorites[-3:]
    recent_trail_favorites = trail_favorites[-3:]
    return recent_trail_favorites, recent_gear_favorites


def get_recent_rated_photos(rated_photos):
    rated_photos.sort(key=get_date_time_added)
    recent_rated = rated_photos[-3:]
    return recent_rated


def get_recent_submitted_photos(submitted_photos):
    submitted_photos.sort(key=get_date_time_added)
    recent_submitted = submitted_photos[-3:]
    return recent_submitted


def get_recent_comments(gear_comments, trail_comments):
    gear_comments.sort(key=get_date_time_added)
    trail_comments.sort(key=get_date_time_added)
    recent_trail_submitted = trail_comments[-3:]
    recent_gear_submitted = gear_comments[-3:]
    return recent_trail_submitted, recent_gear_submitted


# ----------------------------------RETRIEVAL AND ORDERING FUNCTIONS---------------------------------
def get_all_favorites(user_favorites):
    user_favorites.sort(key=get_date_time_added)
    favorites = []
    for favorite in user_favorites:
        if favorite.gear_trail == "Gear":
            new_favorite = Gear.query.filter_by(name=favorite.name).first()
        else:
            new_favorite = Trails.query.filter_by(name=favorite.name).first()
        favorites.append(new_favorite)
    return favorites


def get_photo_ratings(rated_photos):
    one_photos = []
    two_photos = []
    three_photos = []
    four_photos = []
    five_photos = []
    for photo in rated_photos:
        if photo.rating == 1:
            one_photos.append(photo)
        if photo.rating == 2:
            two_photos.append(photo)
        if photo.rating == 3:
            three_photos.append(photo)
        if photo.rating == 4:
            four_photos.append(photo)
        if photo.rating == 5:
            five_photos.append(photo)
    return one_photos, two_photos, three_photos, four_photos, five_photos


def get_ordered_photos(date, photos):
    if date:
        photos.sort(key=get_date_time_added)
        return photos
    else:
        for photo in photos:
            if photo.community_rating == "Be the first to rate this photo!":
                photo.community_rating = "0.0"
        photos.sort(key=get_community_rating, reverse=True)
        return photos


def get_ordered_comments(date, gear_comments, trail_comments):
    if date:
        gear_comments.sort(key=get_date_time_added)
        trail_comments.sort(key=get_date_time_added)
        return gear_comments, trail_comments
    else:
        gear_comments.sort(key=get_parent_post)
        trail_comments.sort(key=get_parent_post)
        return gear_comments, trail_comments


def get_ordered_favorites(gear_favorites, trail_favorites, sort_by):
    if sort_by == "date":
        gear_favorites.sort(key=get_date_time_added)
        trail_favorites.sort(key=get_date_time_added)
    else:
        gear_favorites.sort(key=get_entry_name)
        trail_favorites.sort(key=get_entry_name)
    return gear_favorites, trail_favorites


def get_date_time_added(entry):
    return entry.date_time_added


def get_community_rating(entry):
    return entry.community_rating


def get_parent_post(entry):
    return entry.parent_posts.name


def get_entry_name(entry):
    return entry.name


# -------------------------------------------PHOTO RATING FUNCTIONS----------------------------------------
@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>/rate_photo")
def rate_photo(user_id):
    """
    Allows user to submit a rating for a submitted photo.

    This function first determines if the user has rated this particular photo already. Then it calls the relevant
    function based on that determination before redirecting the user to the page for that trail.
    """

    rating = request.args["rating"]
    photo_id = request.args["photo_id"]
    trail_id = request.args["trail_id"]
    if check_if_already_rated(user_id, photo_id, rating):
        update_photo_rating(photo_id)
        return redirect(url_for("trail_bp.view_trail", db_id=trail_id))
    else:
        add_user_photo_rating(user_id, photo_id, rating)
        update_photo_rating(photo_id)
        return redirect(url_for("trail_bp.view_trail", db_id=trail_id))


def check_if_already_rated(user_id, photo_id, rating):
    """
    Checks if the user has already rated a photo or not.

    Called by the rate_photo function, checks if any of the photos the user has already rated are this photo. If so, the
    function reassigns the rating to the new value and returns True. Otherwise, it simply returns false.

    PARAMETERS
    ----------
    user_id : int
        The id number of an entry in the users table of the database.
    photo_id : str
        The id number of an entry in the trail_pics table of the database. Is sent as a string with the request method.
    rating : str
        A rating between 1-5 assigned by the user. If unassigned, the rating is a string informing the user that the
        photo is unrated, which is why it is not classified as an int.
    """

    user_rated_pics = RatedPhoto.query.filter_by(user_id=user_id).all()
    for pic in user_rated_pics:
        if pic.photo_id == int(photo_id):
            pic.rating = rating
            db.session.commit()
            return True
    return False


def add_user_photo_rating(user_id, photo_id, rating):
    """
    Adds a new entry in the rated_photos table of the database.

    Called by the rate_photo function, this function adds a new photo related to this user to the rated_photos table.

    PARAMETERS
    ----------
    user_id : int
        The id number of an entry in the users table of the database.
    photo_id : str
        The id number of an entry in the trail_pics table of the database. Is sent as a string with the request method.
    rating : str
        A rating between 1-5 assigned by the user. If unassigned, the rating is a string informing the user that the
        photo is unrated, which is why it is not classified as an int.
    """

    new_rating = RatedPhoto(
        rating=rating,
        date_time_added=datetime.now(),
        photo_id=photo_id,
        user_id=user_id
    )
    db.session.add(new_rating)
    db.session.commit()


# --------------------------THIS FUNCTION MIGHT BELONG TO THE TRAILS_BP------------------------------------
def update_photo_rating(photo_id):
    """
    Updates an entry in the rated_photos table of the database.

    Called by the rate_photos function, this function recalculates the average rating a photo has been assigned by all
    users after factoring in the updated rating it has just been assigned.
    """

    photo = TrailPictures.query.get(photo_id)
    ratings_total = 0
    all_ratings = RatedPhoto.query.filter_by(photo_id=photo_id).all()
    for rating in all_ratings:
        ratings_total += float(rating.rating)
    updated_rating = ratings_total / len(all_ratings)
    photo.community_rating = round(updated_rating, 2)
    db.session.commit()


# ----------------------------------FAVORITING FUNCTIONS-----------------------------------------------------
@user_profile_bp.route("/tamarack-treks/user_profile/<user_id>/favorite_trail")
def add_favorite(user_id):
    """
    Adds a new page to the user's favorites.

    Determines what type of database entry (gear, trail, etc) the user is attempting to add to their favorites and
    calls the relevant function based on that determination.
    """

    user = User.query.get(user_id)
    gear_trail = request.args["gear_trail"]
    favorite_id = request.args["favorite_id"]
    if gear_trail == "Gear":
        favorite = Gear.query.get(favorite_id)
    else:
        favorite = Trails.query.get(favorite_id)
    duplicate = create_new_favorite(favorite, user_id)
    if duplicate:
        flash("Already in your favorites.")
        return redirect(url_for('user_profile_bp.view_favorites', user_id=user.id))
    else:
        return redirect(url_for('user_profile_bp.user_profile_dashboard', user_id=user.id))


def create_new_favorite(favorite, user_id):
    """Creates a new entry in the favorites table of the database when called by the add_favorite function."""
    duplicate = False
    user = User.query.get(user_id)
    for old_favorite in user.favorites:
        if favorite.name == old_favorite.name:
            duplicate = True
            return duplicate
    new_favorite = Favorites(
        name=favorite.name,
        favorite_id=favorite.id,
        gear_trail=favorite.gear_trail,
        date_time_added=datetime.now(),
        description=favorite.description,
        user_id=user_id
    )
    if favorite.gear_trail == "Gear":
        new_favorite.img = favorite.img
    else:
        new_favorite.img = favorite.trail_page_pics[0].img
    db.session.add(new_favorite)
    db.session.commit()
    return duplicate
