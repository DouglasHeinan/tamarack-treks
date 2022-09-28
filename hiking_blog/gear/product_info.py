import requests
import lxml
from lxml import etree
from bs4 import BeautifulSoup

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                  "KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,lb;q=0.8,fr;q=0.7"
}


def amazon_info(product_name):
    amazon_url = f"https://www.amazon.com/s?k={product_name}&ref=nb_sb_noss_1"

    # adholder and a-section gets skipped

    response = requests.get(amazon_url, headers=HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    # dom = etree.HTML(str(soup))
    # price = dom.xpath('//*[@id="search"]/div[1]/div[1]/div/span[3]/div[2]/div[5]/div/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div/a/span/span[1]')[0].text
    # price = dom.xpath('//*[@id="search"]/div[1]/div[1]/div/span[3]/div[2]/div[5]/div/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div/a/span/span[2]')[0].text
    # url =
    # link = dom.xpath('//*[@id="search"]/div[1]/div[1]/div/span[3]/div[2]/div[5]/div/div/div/div/div/div[2]/div/div/div[1]/h2/a')[0]
    # url = link.find('a[href]')
    # print(link)

    # !!!!!!!!!Try xpath address?!!!!!!!!!!!!!

    # good_results = soup.find(class_="s-result-item")["class"]
    # good_results.remove("AdHolder")
    # print(good_results)
    # results = soup.find(name=good_results)
    # print(results)
    # print(soup.find(class_="s-result-item")["class"].remove("AdHolder").attrs)

    url = 1
    price = 1

    return url, price


def rei_info(product_name):
    rei_url = f"https://www.rei.com/search?q={product_name}"

    response = requests.get(rei_url, headers=HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    # dom = etree.HTML(str(soup))
    # price = dom.xpath('//*[@id="search-results"]/ul/li[1]/div[3]/div/div/div/span').text
    # print(soup.find("li"))

    url = 1
    price = 1

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
