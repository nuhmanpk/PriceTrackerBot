import asyncio
import threading
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os
import schedule
import time
import pytz
import re

from scraper import scrape
from scheduler import check_prices
from helpers import fetch_all_products, add_new_product, fetch_one_product, delete_one
from regex_patterns import flipkart_url_patterns, amazon_url_patterns, all_url_patterns

load_dotenv()

timezone = pytz.timezone("Asia/Kolkata")


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
    text = (
        "🤖 **Price Tracker Bot Help**\n\n"
        "Here are the available commands:\n"
        "1. `/my_trackings`: View all the products you are currently tracking.\n"
        "2. `/stop < product_id >`: Stop tracking a specific product. Replace `<product_id>` with the product ID you want to stop tracking.\n"
        "3. `/product < product_id >`: Get detailed information about a specific product. Replace `<product_id>` with the product ID you want information about.\n"
        "\n\n**How It Works:**\n\n"
        "1. Send the product link from Flipkart.\n"
        "2. The bot will automatically scrape and track the product.\n"
        "3. If there is a price change, the bot will notify you with the updated information.\n"
        "Feel free to use the commands and start tracking your favorite products!\n"
    )
    await message.reply_text(text, quote=True)


@app.on_message(filters.command("my_trackings") & filters.private)
async def track(_, message):
    try:
        chat_id = message.chat.id
        text = await message.reply_text("Fetching Your Products...")
        products = await fetch_all_products(chat_id)
        if products:
            products_message = "Your Tracked Products:\n\n"

            for i, product in enumerate(products, start=1):
                _id = product.get("product_id")
                product_name = product.get("product_name")
                product_url = product.get("url")
                product_price = product.get("price")

                products_message += (
                    f"🏷️ **Product {i}**: [{product_name}]({product_url})\n\n"
                )
                products_message += f"💰 **Current Price**: {product_price}\n"
                products_message += f"❌ Use `/stop {_id}` to Stop tracking\n\n"

            await text.edit(products_message, disable_web_page_preview=True)
        else:
            await text.edit("No products added yet")
    except Exception as e:
        print(e)


@app.on_message(filters.regex("|".join(all_url_patterns)))
async def track_flipkart_url(_, message):
    try:
        url = message.text
        platform = "amazon" if any(re.match(pattern, url) for pattern in amazon_url_patterns) else "flipkart"
        product_name, price = await scrape(url, platform)
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
                    f"🛍 **Product:** [{product_name}]({product_url})\n\n"
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
            is_deleted = await delete_one(id, chat_id)
            if is_deleted:
                await status.edit("Product Deleted from Your Tracking List")
            else:
                await status.edit("Failed to Delete the product")
        else:
            await status.edit("Failed to Delete the product")
    except Exception as e:
        print(e)


schedule.every().day.at("00:00").do(lambda: asyncio.run(check_prices(app))).tag(
    "daily_job"
)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(5)


def main():
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()

    app.run(print("Bot Running"))


if __name__ == "__main__":
    main()
