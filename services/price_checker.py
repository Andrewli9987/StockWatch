from decimal import Decimal

from sqlalchemy.orm import Session

from models import ProductDB
from services.price_service import update_product_price
from services.price_fetcher import fetch_product_price

def check_product_price(
        db: Session,
        product_id: int
):
    # Step 1: Find the product
    product = db.get(ProductDB, product_id)

    if product is None:
        raise ValueError("Product not found")

    # Step 2: Make sure the product has a URL
    if not product.product_url:
        raise ValueError("Product URL is missing")

    # Step 3: Fetch the latest price
    latest_price = fetch_product_price(
        product.product_url
    )

    # Step 4: Compare prices
    current_price = Decimal(str(product.price))

    if latest_price == current_price:
        return {
            "product_id": product.id,
            "price_changed": False,
            "current_price": current_price
        }

    # Step 5: Check if price history already exists
    update_product_price(
        db,
        product,
        latest_price
    )

    # Step 6: Save original price is no history exists
    db.commit()
    db.refresh(product)

    return {
        "product_id": product.id,
        "price_changed": True,
        "old_price": current_price,
        "new_price": latest_price
    }

    # Step 7: Save the new price
    db.add(
        PriceHistoryDB(
            product_id=product.id,
            price=latest_price
        )
    )

    # Step 8: Update the product price
    product.price = latest_price

    # Step 9: Commit everything to PostgreSQL
    db.commit()
    db.refresh(product)

    return {
        "product_id": product.id,
        "price_changed": True,
        "old_price": current_price,
        "new_price": latest_price
    }