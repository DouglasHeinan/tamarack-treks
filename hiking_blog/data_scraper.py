"""Contains functions for automated site updates and maintenance"""
from flask import Flask
import shutil
import time
import os
from hiking_blog import db, login_manager


def app_updates():
    """

    After setting up an application object so as to work within the Flask app context, this function automates some
    aspects of site maintenance. Specifically, it triggers a function that will delete all submitted photo files that
    are more than a month old, and a separate function to change the price of a piece of gear in the database. Further,
    if the latter function fails to scrape the price from a database, this function triggers another function that will
    notify the admins of dead links that have been found.
    """

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
    Checks the current price of every piece of gear in the database and changes the displayed price on the app.

    This function iterates through every piece of gear in the database and runs the update_gear_links function to keep
    the entry in the database current.
    """

    dead_link_change = False
    for gear_piece in all_gear:
        dead_link_change, gear_piece.moosejaw_price, gear_piece.moosejaw_link_dead, gear_piece.moosejaw_out_of_stock = \
            update_gear_links(gear_piece.moosejaw_price, gear_piece.moosejaw_link_dead,
                              gear_piece.moosejaw_out_of_stock, gear_piece.moosejaw_url, moosejaw_price_query,
                              dead_link_change)
        dead_link_change, gear_piece.rei_price, gear_piece.rei_link_dead, gear_piece.rei_out_of_stock = \
            update_gear_links(gear_piece.rei_price, gear_piece.rei_link_dead, gear_piece.rei_out_of_stock,
                              gear_piece.rei_url, rei_price_query, dead_link_change)
        dead_link_change, gear_piece.backcountry_price, gear_piece.backcountry_link_dead, \
            gear_piece.backcountry_out_of_stock = \
            update_gear_links(gear_piece.backcountry_price, gear_piece.backcountry_link_dead,
                              gear_piece.backcountry_out_of_stock, gear_piece.backcountry_url, backcountry_price_query,
                              dead_link_change)
        db.db.session.commit()
    return dead_link_change


def update_gear_links(price, dead_link, out_of_stock, url, price_query, dead_link_change):
    """
    Updates a gear listing in the database.

    For one entry in the gear table of the database, this function updates the price listed by one of the three
    retailers (Moosejaw, Backcountry, or REI) in the database. If, for some reason, the price cannot be scraped, the
    entry is updated to denote that the link is dead, if it hasn't already.
    """
    back_in_stock = True
    if price != "" and not dead_link:
        try:
            price = price_query(url)
        except AttributeError:
            back_in_stock = False
            if not out_of_stock:
                dead_link = True
                dead_link_change = True
            else:
                pass
    if back_in_stock:
        out_of_stock = False
    return dead_link_change, price, dead_link, out_of_stock


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
