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

        global_products = []
        for product in products:
            global_product = global_collection.find_one(
                {"_id": product.get("product_id")}
            )
            global_products.append(global_product)

        return global_products

    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return []


async def fetch_one_product(_id):
    try:
        product = collection.find_one({"_id": ObjectId(_id)})
        global_product = global_collection.find_one({"_id": product.get("product_id")})
        return global_product

    except Exception as e:
        print(f"Error fetching product: {str(e)}")
        return None


async def add_new_product(user_id, product_name, product_url, initial_price):
    try:
        existing_global_product = global_collection.find_one(
            {"product_name": product_name}
        )

        if not existing_global_product:
            global_new_product = {
                "user_id": user_id,
                "product_name": product_name,
                "url": product_url,
                "price": initial_price,
                "upper": initial_price,
                "lower": initial_price,
            }
            new_global_product = global_collection.insert_one(global_new_product)

            existing_product = collection.find_one(
                {"user_id": user_id, "product_id": new_global_product.inserted_id}
            )

            if existing_product:
                print("Product already exists.")
                return existing_product["_id"]

            new_local_product = {
                "user_id": user_id,
                "product_id": new_global_product.inserted_id,
            }

            result = collection.insert_one(new_local_product)

        print("Product added successfully.")
        return result.inserted_id

    except Exception as e:
        print(f"Error adding product: {str(e)}")
        return None


async def update_product_price(id, new_price):
    try:
        global_product = global_collection.find_one(
            {"_id": id},
        )

        if global_product:
            upper_price = global_product.get("upper", new_price)
            lower_price = global_product.get("lower", new_price)

            if new_price > upper_price:
                upper_price = new_price
            elif new_price < lower_price:
                lower_price = new_price

            global_collection.update_one(
                {"_id": id},
                {
                    "$set": {
                        "price": new_price,
                        "upper": upper_price,
                        "lower": lower_price,
                    }
                },
            )
            print("Global product prices updated successfully.")
    except Exception as e:
        print(f"Error updating product price: {str(e)}")


async def delete_one(_id, user_id):
    try:
        product = collection.find_one({"_id": ObjectId(_id)})

        if product and product.get("user_id") == int(user_id):
            collection.delete_one({"_id": ObjectId(_id)})
            return True
        else:
            return None

    except Exception as e:
        print(f"Error deleting product: {str(e)}")
        return None
