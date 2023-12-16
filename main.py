from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os

from scraper import scrape
from scheduler import check_prices
from helpers import (fetch_all_products, add_new_product, fetch_one_product, delete_one)
from regex_patterns import flipkart_url_patterns

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

app = Client("PriceTrackerBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


@app.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    text = (
        f"Hello {message.chat.username}! 🌟\n\n"
        "I'm PriceTrackerBot, your personal assistant for tracking product prices. 💸\n\n"
        "To get started, use the /my_trackings command to start tracking a product. "
        "Simply send the url:\n"
        "For example:\n"
        "I'll keep you updated on any price changes for the products you're tracking. "
        "Feel free to ask for help with the /help command at any time. Happy tracking! 🚀"
    )

    await message.reply_text(text, quote=True)

@app.on_message(filters.command("help") & filters.private)
async def help(_, message: Message):
    await check_prices()

@app.on_message(filters.command("my_trackings") & filters.private)
async def track(_, message):
    try:
        chat_id = message.chat.id
        text = await message.reply_text("Fetching Your Products...")
        products = await fetch_all_products(chat_id)
        if products:
            products_message = "Your Tracked Products:\n\n"

            for i, product in enumerate(products, start=1):
                _id = product.get("_id")
                product_name = product.get("product_name")
                product_url = product.get("url")
                product_price = product.get("price")

                products_message += (
                    f"🏷️ **Product {i}**: [{product_name}]({product_url})\n"
                )
                products_message += f"💰 **Current Price**: {product_price}\n"
                products_message += f"❌ Use `/stop {_id}` to Stop tracking\n\n"

            await text.edit(products_message, disable_web_page_preview=True)
        else:
            await text.edit("No products added yet")
    except Exception as e:
        print(e)


@app.on_message(filters.regex("|".join(flipkart_url_patterns)))
async def track_flipkart_url(_, message):
    try:
        product_name, price = await scrape(message.text)
        status = await message.reply_text("Adding Your Product... Please Wait!!")
        if product_name and price:
            id = await add_new_product(
                message.chat.id, product_name, message.text, price
            )
            await status.edit(
                f'Tracking your product "{product_name}"!\n\n'
                f"You can use\n `/product {id}` to get more information about it."
            )
        else:
            await status.edit("Failed to scrape !!!")
    except Exception as e:
        print(e)


@app.on_message(filters.command("product") & filters.private)
async def track_product(_, message):
    try:
        __, id = message.text.split()
        status = await message.reply_text("Getting Product Info....")
        if id:
            product = await fetch_one_product(id)
            if product:
                product_name = product.get("product_name")
                product_url = product.get("url")
                product_price = product.get("price")
                maximum_price = product.get("upper")
                minimum_price = product.get("lower")

                products_message = (
                    f"🛍 **Product:** [{product_name}]({product_url})\n"
                    f"💲 **Current Price:** {product_price}\n"
                    f"📉 **Lowest Price:** {minimum_price}\n"
                    f"📈 **Highest Price:** {maximum_price}\n"
                    f"\n\n\nTo Stop Tracking, use `/stop {id}`"
                )

                await status.edit(products_message, disable_web_page_preview=True)
            else:
                await status.edit("Product Not Found")
        else:
            await status.edit("Failed to fetch the product")
    except Exception as e:
        print(e)

@app.on_message(filters.command("stop") & filters.private)
async def delete_product(_, message):
    try:
        __, id = message.text.split()
        status = await message.reply_text("Deleting Product....")
        chat_id = message.chat.id
        if id:
            is_deleted = await delete_one(id,chat_id)
            if is_deleted:
                await status.edit("Product Deleted from Your Tracking List")
            else:
                await status.edit("Failed to Delete the product")
        else:
            await status.edit("Failed to Delete the product")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    app.run(print("Bot Running..."))
