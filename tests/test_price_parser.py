import pytest

from decimal import Decimal



from services.price_parser import extract_price


def test_extract_valid_price():
    html = '<p class="price_color">£51.77</p>'

    result = extract_price(html)

    assert result == Decimal("51.77")

def test_extract_price_with_comma():
    html = '<p class="price_color">£1,299.99</p>'

    result = extract_price(html)

    assert result == Decimal("1299.99")

def test_extract_missing_price():
    html = "<div>No price available</div>"

    with pytest.raises(ValueError, match="Price element not found"):
        extract_price(html)

def test_extract_invalid_price():
    html = '<p class="price_color">Not Available</p>'

    with pytest.raises(ValueError, match="Invalid price format"):
        extract_price(html)

def test_extract_negative_price():
    html = '<p class= "price_color"> £-10.00</p>'

    with pytest.raises(ValueError, match="Price must be a positive number"):
        extract_price(html)



