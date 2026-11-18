from decimal import Decimal

def fetch_product_price(product_url: str) -> Decimal:
    """
    Simulate fetching a product price from a URL.
    Real website integration will come later.
    """

    if not product_url:
        raise ValueError("Product URL is required")

    return Decimal("199.99")