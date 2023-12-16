from pyrogram import Client

from scraper import scrape_price
from scheduler import check_prices
from dotenv import load_dotenv
import os

bot_token = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

app = Client("PriceTrackerBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

if __name__ == "__main__":
    app.run()
    check_prices()
