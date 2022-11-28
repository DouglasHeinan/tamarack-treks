"""Contains functions for automated site updates and maintenance"""
from flask import Flask
import shutil
import time
import os
from hiking_blog import db, login_manager


def app_updates():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    login_manager.create_login_manager(app)

    with app.app_context():
        db.init_db(app)

        from hiking_blog.gear import gear

        app.register_blueprint(gear.gear_bp)

        from hiking_blog.models import Gear
        from hiking_blog.gear.gear_prices import moosejaw_price_query, rei_price_query, backcountry_price_query
        from hiking_blog.contact import send_dead_links

        while True:
            print("starting")
            all_gear = Gear.query.all()
            parent_path = f"hiking_blog/admin/static"
            all_folders = os.listdir(parent_path)
            dead_link_change = check_prices(all_gear, moosejaw_price_query, rei_price_query, backcountry_price_query)
            if dead_link_change:
                send_dead_links()
            delete_old_files(all_folders, parent_path)
            print("waiting...")
            time.sleep(30)


def check_prices(all_gear, moosejaw_price_query, rei_price_query, backcountry_price_query):
    """
    Updates prices in the gear table.

    Iterates through every entry in the gear table and scrapes the links associated with the three major retailers for
    the product's current price. It then updates the price in the database. If the link is dead, adds the link to a
    list to be emailed to an admin so the link can be updated. In this event, the price in the database will remain
    unchanged.

    PARAMETERS
    ----------
    all_gear : list
        A list of all gear entires in the database.
    moosejaw_price_query : function
        A function that scrapes the product page on moosejaw for the current price.
    rei_price_query : function
        A function that scrapes the product page on rei for the current price.
    backcountry_price_query : function
    A function that scrapes the product page on backcountry for the current price.

    """
    dead_link_change = False
    for gear_piece in all_gear:
        if gear_piece.moosejaw_price != "" and gear_piece.moosejaw_link_dead == False:
            try:
                gear_piece.moosejaw_price = moosejaw_price_query(gear_piece.moosejaw_url)
            except AttributeError:
                gear_piece.moosejaw_link_dead = True
                dead_link_change = True
        if gear_piece.rei_price != "":
            try:
                gear_piece.rei_price = rei_price_query(gear_piece.rei_url)
            except AttributeError:
                gear_piece.rei_link_dead = True
                dead_link_change = True
        if gear_piece.backcountry_price != "":
            try:
                gear_piece.backcountry_price = backcountry_price_query(gear_piece.backcountry_url)
            except AttributeError:
                gear_piece.backcountry_link_dead = True
        db.db.session.commit()
    return dead_link_change


def delete_old_files(all_folders, parent_path):
    """
    Deletes all photo files thirty days after creation time in static folder sub-directories.

    This function iterates through the approved, save_for_appeal_pics, and submitted_trail_pics directories and deletes
    any sub-directories that were created thirty or more days ago.

    PARAMETERS
    ----------
    all_folders : list
        A list of the three directories: approved, save_for_appeal_pics, and submitted_trail_pics.
    parent_path : str
        The file path preceding the names of the three folders.
    """

    current_time = time.time()
    for directory in all_folders:
        directories_queued_for_deletion = os.listdir(f"{parent_path}/{directory}")
        for old_folder in directories_queued_for_deletion:
            full_path = f"{parent_path}/{directory}/{old_folder}"
            creation_time = os.path.getctime(full_path)
            if (current_time - creation_time) // (24 * 3600) >= 30:
                shutil.rmtree(full_path)


if __name__ == "__main__":
    app_updates()
