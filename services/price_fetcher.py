import requests
from decimal import Decimal
from urllib.parse import urlparse

from services.price_parser import extract_price

def fetch_product_price(product_url: str) -> Decimal:
    if not product_url:
        raise ValueError("Product URL is required")

    parsed_url = urlparse(product_url)

    # For now, support only our practice website
    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != "books.toscrape.com"
        or parsed_url.username is not None
        or parsed_url.password is not None
        or parsed_url.port is not None
    ):
        raise ValueError("Unsupported product URL")

    response = requests.get(
        product_url,
        timeout=10,
        allow_redirects=False,
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    return extract_price(response.text)

