from decimal import Decimal, InvalidOperation
from bs4 import BeautifulSoup

def extract_price(html: str) -> Decimal:
    soup = BeautifulSoup(html, "html.parser")

    # Find the price element
    price_element = soup.select_one(".price_color")

    if price_element is None:
        raise ValueError("Price element not found")

    # Extract the text
    price_text = price_element.get_text(strip=True)

    # Clean the price
    clean_price = (
        price_text
        .replace("£", "")
        .replace(",", "")
        .strip()
    )

    # Convert the Decimal
    try:
        price = Decimal(clean_price)
    except InvalidOperation:
        raise ValueError("Invalid price format")

    if not price.is_finite() or price <= 0:
        raise ValueError("Price must be a positive number")

    return price