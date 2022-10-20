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

        while True:
            print("Doing the thing.")
            all_gear = Gear.query.all()
            parent_path = f"hiking_blog/admin/static"
            all_folders = os.listdir(parent_path)
            check_prices(all_gear, moosejaw_price_query, rei_price_query, backcountry_price_query)
            delete_old_files(all_folders, parent_path)
            time.sleep(30)


def check_prices(all_gear, moosejaw_price_query, rei_price_query, backcountry_price_query):
    for gear_piece in all_gear:
        if gear_piece.moosejaw_price is not None:
            gear_piece.moosejaw_price = moosejaw_price_query(gear_piece.moosejaw_url)
        if gear_piece.rei_price is not None:
            gear_piece.rei_price = rei_price_query(gear_piece.rei_url)
        if gear_piece.backcountry_price is not None:
            gear_piece.backcountry_price = backcountry_price_query(gear_piece.backcountry_url)
        db.db.session.commit()
        print(f"Made changes to {gear_piece.name}.")


def delete_old_files(all_folders, parent_path):
    current_time = time.time()
    for directory in all_folders:
        directories_queued_for_deletion = os.listdir(f"{parent_path}/{directory}")
        for old_folder in directories_queued_for_deletion:
            full_path = f"{parent_path}/{directory}/{old_folder}"
            creation_time = os.path.getctime(full_path)
            print(f"Creation time for {old_folder}: {time.ctime(creation_time)}")
            if (current_time - creation_time) // (24 * 3600) >= 3:
                shutil.rmtree(full_path)
                print(f"Directory {str(old_folder)} removed")
            else:
                print(f"Kept {old_folder}")
        print(f"Finished with {directory}")
    print(f"Finished with {all_folders}")


if __name__ == "__main__":
    app_updates()
