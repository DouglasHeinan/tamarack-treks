# from threading import Thread
#
#
# def async_update_gear_info(function):
#     thread = Thread(target=function)
#     thread.daemon = True
#     thread.start()

"""Contains the functions that determine the price of a piece of gear from three major retailers."""
import requests
from hiking_blog.db import db
from hiking_blog.models import Gear
from bs4 import BeautifulSoup
# from apscheduler.schedulers.background import BackgroundScheduler
# from flask import current_app as app
import time
from datetime import datetime


HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,lb;q=0.8,fr;q=0.7"
}


# def delete_this():
#     while True:
#         if datetime.now().second == 30:
#             print("Bottom of the minute")
#             time.sleep(15)


# def update_gear_info(function):
#     scheduler = BackgroundScheduler(daemon=True)
#     scheduler.add_job(function, "interval", seconds=5)
#     scheduler.start()
#     while True:
#         sleep(1)


def update_gear_prices():
    print(db)
    print(Gear)
    time.sleep(30)
    while True:
        if datetime.now().second == 30:
            print("Doing the thing.")
            all_gear = Gear.query.all()
            for gear_piece in all_gear:
                if gear_piece.moosejaw_price is not None:
                    gear_piece.moosejaw_price = moosejaw_price_query(gear_piece.moosejaw_url)
                if gear_piece.rei_price is not None:
                    gear_piece.rei_price = rei_price_query(gear_piece.rei_url)
                if gear_piece.backcountry_price is not None:
                    gear_piece.backcountry_price = backcountry_price_query(gear_piece.backcountry_url)
                db.session.commit()
                time.sleep(20)


def moosejaw_price_query(moosejaw_url):
    """Scrapes the Amazon page of the requested gear piece and returns its price"""

    response = requests.get(moosejaw_url, headers=HEADER)
    soup = BeautifulSoup(response.text, features="lxml")
    gear_price = soup.find(class_="price-option").getText()

    return gear_price


def rei_price_query(rei_url):
    """Scrapes the REI page of the requested gear piece and returns its price"""

    response = requests.get(rei_url, headers=HEADER)
    soup = BeautifulSoup(response.text, features="lxml")
    gear_price = soup.find(class_="price-value").getText()

    return gear_price


def backcountry_price_query(backcountry_url):
    """Scrapes the Backcountry page of the requested gear piece and returns its price"""

    response = requests.get(backcountry_url, headers=HEADER)
    soup = BeautifulSoup(response.text, features="lxml")
    gear_price = soup.find(class_="css-17wknbl").getText()

    return gear_price
