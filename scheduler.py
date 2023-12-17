import time
from pymongo import MongoClient
import os
from scraper import scrape
from dotenv import load_dotenv

load_dotenv()


dbclient = MongoClient(os.getenv("MONGO_URI"))
database = dbclient[os.getenv("DATABASE")]
PRODUCTS = database[os.getenv("PRODUCTS")]


async def check_prices():
    print("Checking Price for Products...")
    for product in PRODUCTS.find():
        _, current_price = await scrape(product["url"])
        time.sleep(1)
        if current_price is not None:
            if current_price != product["price"]:
                PRODUCTS.update_one(
                    {"_id": product["_id"]},
                    {
                        "$set": {
                            "price": current_price,
                            "lower": current_price
                            if current_price < product["lower"]
                            else product["lower"],
                            "upper": current_price
                            if current_price > product["upper"]
                            else product["upper"],
                        }
                    },
                )
    print("Completed")
