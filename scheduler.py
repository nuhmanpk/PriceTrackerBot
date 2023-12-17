import time
from pymongo import MongoClient
import os
from scraper import scrape
from dotenv import load_dotenv

load_dotenv()


dbclient = MongoClient(os.getenv("MONGO_URI"))
database = dbclient[os.getenv("DATABASE")]
collection = database[os.getenv("COLLECTION")]
PRODUCTS = database[os.getenv("PRODUCTS")]


async def check_prices(app):
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
                            "previous_price": product["price"],
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
    changed_products = await compare_prices()
    for changed_product in changed_products:
        cursor = collection.find({"product_id": changed_product})
        users = list(cursor)
        for user in users:
            product = PRODUCTS.find_one({"_id": user.get("product_id")})
            percentage_change = (
                (product["price"] - product["previous_price"])
                / product["previous_price"]
            ) * 100
            text = (
                f"🎉 Good news! The price of {product['product_name']} has changed.\n"
                f"   - Previous Price: ₹{product['previous_price']:.2f}\n"
                f"   - Current Price: ₹{product['price']:.2f}\n"
                f"   - Percentage Change: {percentage_change:.2f}%\n"
                f"   - [Check it out here]({product['url']})"
            )
            await app.send_message(
                chat_id=user.get("user_id"), text=text, disable_web_page_preview=True
            )


async def compare_prices():
    print("Comparing Prices...")
    product_with_changes = []
    for product in PRODUCTS.find():
        current_price = product.get("price")
        previous_price = product.get("previous_price")
        if current_price != previous_price:
            product_with_changes.append(product.get("_id"))

    return product_with_changes
