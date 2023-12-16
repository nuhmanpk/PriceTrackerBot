import requests
from bs4 import BeautifulSoup

def scrape_price(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Implement scraping logic based on the structure of the website
        # This is a simplified example; adjust based on the actual structure of the website

        # Example for Amazon
        price_element = soup.find("span", {"id": "priceblock_ourprice"})
        if price_element:
            price = float(price_element.text.replace("₹", "").replace(",", "").strip())
            return price

        # Example for Flipkart
        # Add similar logic for Flipkart

    except Exception as e:
        print(f"Error scraping price: {str(e)}")
    return None
