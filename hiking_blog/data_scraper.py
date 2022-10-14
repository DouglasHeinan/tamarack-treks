# """Contains the functions that determine the price of a piece of gear from three major retailers."""

from flask import Flask
import time
from hiking_blog import db, login_manager


def update_gear_prices():
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
            for gear_piece in all_gear:
                if gear_piece.moosejaw_price is not None:
                    gear_piece.moosejaw_price = moosejaw_price_query(gear_piece.moosejaw_url)
                if gear_piece.rei_price is not None:
                    gear_piece.rei_price = rei_price_query(gear_piece.rei_url)
                if gear_piece.backcountry_price is not None:
                    gear_piece.backcountry_price = backcountry_price_query(gear_piece.backcountry_url)
                db.db.session.commit()
            time.sleep(30)


if __name__ == "__main__":
    update_gear_prices()
