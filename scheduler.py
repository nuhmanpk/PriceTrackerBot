import time
from pymongo import MongoClient
import os
from scraper import scrape
from dotenv import load_dotenv

load_dotenv()


dbclient = MongoClient(os.getenv("MONGO_URI"))
database = dbclient[os.getenv("DATABASE")]
global_collection = database[os.getenv("GLOBAL_COLLECTION")]


async def check_prices():
    for product in global_collection.find():
        _, current_price = await scrape(product["url"])
        
        if current_price is not None:
            
            if current_price != product["price"]:
                global_collection.update_one(
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
    print('Completed')
