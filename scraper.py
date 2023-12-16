import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

price_class = os.getenv("PRICE_CLASS")
product_name_class = os.getenv("PRODUCT_NAME_CLASS")


async def scrape(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        price = await scrape_price(soup)
        product_name = await scrape_name(soup)
        return product_name, price
    except Exception as e:
        print(e)
        return None


async def scrape_price(soup):
    try:
        price_element = soup.find("div", {"class": price_class})
        if price_element:
            price = float(price_element.text.replace("₹", "").replace(",", "").strip())
            return price
    except Exception as e:
        print(f"Error scraping price: {str(e)}")
    return None


async def scrape_name(soup):
    try:
        name_element = soup.find("span", {"class": product_name_class})
        if name_element:
            return name_element.text.strip()
    except Exception as e:
        print(f"Error scraping name: {str(e)}")
    return None
