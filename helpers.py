from pymongo import MongoClient
import os
from bson import ObjectId

dbclient = MongoClient(os.getenv("MONGO_URI"))
database = dbclient[os.getenv("DATABASE")]
collection = database[os.getenv("COLLECTION")]
global_collection = database[os.getenv("GLOBAL_COLLECTION")]



async def fetch_all_products(user_id):
    try:
        cursor = collection.find({"user_id": user_id})
        products = list(cursor)
        return products

    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return []


async def fetch_one_product(_id):
    try:
        product = collection.find_one({"_id": ObjectId(_id)})
        return product

    except Exception as e:
        print(f"Error fetching product: {str(e)}")
        return None


async def add_new_product(user_id, product_name, product_url, initial_price):
    try:
        existing_product = collection.find_one(
            {"user_id": user_id, "product_name": product_name, "url": product_url}
        )

        if existing_product:
            print("Product already exists.")
            return existing_product["_id"]
                

        new_product = {
            "user_id": user_id,
            "product_name": product_name,
            "url": product_url,
            "price": initial_price,
        }

        result = collection.insert_one(new_product)
        
        global_new_product = {
            "user_id": user_id,
            "product_name": product_name,
            "url": product_url,
            "price": initial_price,
            "upper": initial_price,
            "lower": initial_price
        }
        
        existing_global_product = global_collection.find_one({"product_name": product_name})
        if not existing_global_product:
                global_collection.insert_one(global_new_product)
                
        
        print("Product added successfully.")
        return result.inserted_id

    except Exception as e:
        print(f"Error adding product: {str(e)}")
        return None


async def update_product_price(user_id, product_name, new_price):
    try:
        collection.update_one(
            {"user_id": user_id, "product_name": product_name},
            {"$set": {"price": new_price}},
        )
        print("Product price updated successfully.")
        
        global_product = global_collection.find_one({"product_name": product_name})

        if global_product:
                upper_price = global_product.get("upper", new_price)
                lower_price = global_product.get("lower", new_price)

                if new_price > upper_price:
                    upper_price = new_price
                elif new_price < lower_price:
                    lower_price = new_price

                # Update the global product
                global_collection.update_one(
                    {"product_name": product_name},
                    {"$set": {"price": new_price, "upper": upper_price, "lower": lower_price}},
                )
                print("Global product prices updated successfully.")
    except Exception as e:
        print(f"Error updating product price: {str(e)}")
