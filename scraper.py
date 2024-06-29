from python_flipkart_scraper import ExtractFlipkart


async def scrape(url):
    try:
        product = ExtractFlipkart(url)
        price = product.get_price()
        product_name = product.get_title()
        return product_name, price
    except Exception as e:
        print(e)
        return None, None