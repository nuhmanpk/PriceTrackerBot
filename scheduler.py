import time
from pymongo import MongoClient
import os
from scraper import scrape_price
from main import app

dbclient = MongoClient(os.getenv('MONGO_URI'))
database = dbclient[os.getenv('DATABASE')]
collection = database[os.getenv('COLLECTION')]

def check_prices():
    while True:
        # Check prices every 24 hours (adjust as needed)
        time.sleep(24 * 60 * 60)

        for product in collection.find():
            current_price = scrape_price(product["url"])
            if current_price is not None and current_price < product["price"]:
                # Send alert to the user
                app.send_message(product["user_id"], f"Price alert!\n{product['product_name']} is now {current_price}!")

                # Update the stored price in MongoDB
                collection.update_one({"_id": product["_id"]}, {"$set": {"price": current_price}})
