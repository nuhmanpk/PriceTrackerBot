from python_flipkart_scraper import ExtractFlipkart
from python_amazon_scraper import ExtractAmazon

async def scrape(url, platform):
    try:
        if platform == "flipkart":
            product = ExtractFlipkart(url)
        elif platform == "amazon":
            product = ExtractAmazon(url)
        else:
            raise ValueError("Unsupported platform")

        price = product.get_price()
        product_name = product.get_title()
        return product_name, price
    except Exception as e:
        print(e)
        return None, None
