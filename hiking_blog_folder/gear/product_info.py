import requests
import lxml
from bs4 import BeautifulSoup


def amazon_info(product_name):
    amazon_url = f"https://www.amazon.com/s?k={product_name}&ref=nb_sb_noss_1"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                      "KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,lb;q=0.8,fr;q=0.7"
    }

    response = requests.get(amazon_url, headers=header)
    soup = BeautifulSoup(response.text, "lxml")

    # price = soup.find(class_="a-offscreen").getText()
    # print(f"The price is: {price}")

    # all_results = soup.find(class_="s-search-results")
    # unwanted = all_results.find(class_="a-section")
    # ads = all_results.find(class_="AdHolder")
    # unwanted.extract()
    # ads.extract()

    good_results = soup.find(class_="s-result-item")["class"]
    good_results.remove("AdHolder")
    print(good_results)
    results = soup.find(name=good_results)
    print(results)
    # print(soup.find(class_="s-result-item")["class"].remove("AdHolder").attrs)

    url = 1
    price = 1

    return url, price


def rei_info(product_name):
    rei_url = f"https://www.rei.com/search?q={product_name}"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                      "KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,lb;q=0.8,fr;q=0.7"
    }

    response = requests.get(rei_url, headers=header)
    soup = BeautifulSoup(response.text, "lxml")

    url = 1
    price = 1



    # adholder and a-section gets skipped

    return url, price


def backcountry_info(product_name):
    backcountry_url = f"https://www.backcountry.com/search?s=u&q={product_name}"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                      "KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,lb;q=0.8,fr;q=0.7"
    }

    response = requests.get(backcountry_url, headers=header)
    soup = BeautifulSoup(response.text, "lxml")

    url = 1
    price = 1

    return url, price

