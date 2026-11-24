import pytest
import requests

from decimal import Decimal
from unittest.mock import patch, Mock

from services.price_fetcher import fetch_product_price

def test_fetch_product_price_success():
    # Create a fake HTTP response
    mock_response = Mock()

    mock_response.text = (
        '<p class ="price_color">£51.77</p>'
    )

    mock_response.status_code = 200

    # Replace requests.get temporarily
    with patch("services.price_fetcher.requests.get") as mock_get:
        mock_get.return_value = mock_response

        result = fetch_product_price(
            "https://books.toscrape.com/"
        )

    assert result == Decimal("51.77")
    mock_get.assert_called_once_with(
        "https://books.toscrape.com/",
        timeout=10,
        allow_redirects=False
    )

def test_fetch_product_price_missing_url():
    with pytest.raises(ValueError, match="Product URL is required"):
        fetch_product_price("")

def test_fetch_product_price_unsupported_url():
    with pytest.raises(ValueError, match="Unsupported product URL"):
        fetch_product_price("https://example.com/product")

def test_fetch_product_price_http_error():
    mock_response = Mock()

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("404 Not Found")
    )

    with patch("services.price_fetcher.requests.get") as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            fetch_product_price("https://books.toscrape.com/")
