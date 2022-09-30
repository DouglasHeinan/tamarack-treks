"""Contains the functions that determine the price of a piece of gear from three major retailers."""
import requests
from bs4 import BeautifulSoup

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,lb;q=0.8,fr;q=0.7"
}


def amazon_price_query(amazon_url):
    """Scrapes the Amazon page of the requested gear piece and returns its price"""

    response = requests.get(amazon_url, headers=HEADER)
    soup = BeautifulSoup(response.text)
    gear_price = soup.find(class_="a-offscreen").getText()

    return gear_price


def rei_price_query(rei_url):
    """Scrapes the REI page of the requested gear piece and returns its price"""

    response = requests.get(rei_url, headers=HEADER)
    soup = BeautifulSoup(response.text)
    gear_price = soup.find(class_="price-value").getText()

    return gear_price


def backcountry_price_query(backcountry_url):
    """Scrapes the Backcountry page of the requested gear piece and returns its price"""

    response = requests.get(backcountry_url, headers=HEADER)
    soup = BeautifulSoup(response.text)
    gear_price = soup.find(class_="css-17wknbl").getText()

    return gear_price
