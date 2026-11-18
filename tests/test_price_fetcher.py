import pytest
from decimal import Decimal

from services.price_fetcher import fetch_product_price

def test_fetch_product_price():
    price = fetch_product_price(
        "https://example.com.monitor"
    )

    assert price == Decimal("199.99")
    assert isinstance(price, Decimal)

def test_fetch_product_price_without_url():
    with pytest.raises(ValueError):
        fetch_product_price("")