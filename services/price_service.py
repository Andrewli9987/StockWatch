from decimal import Decimal

from sqlalchemy.orm import Session

from models import ProductDB, PriceHistoryDB

def update_product_price(
    db: Session,
    product: ProductDB,
    new_price: Decimal
) -> bool:
    old_price = Decimal(str(product.price))
    new_price = Decimal(str(new_price))

    # No change means no history eed to be recorded
    if old_price == new_price:
        return False

    # Check whether history already exists
    existing_history = (
        db.query(PriceHistoryDB)
        .filter(PriceHistoryDB.product_id==product.id)
        .first()
    )

    # Record the original price only once
    if existing_history is None:
        db.add(
            PriceHistoryDB(
                product_id=product.id,
                price = old_price
            )
        )

    # Record the new price
    db.add(
        PriceHistoryDB(
            product_id=product.id,
            price = new_price
        )
    )

    # Update the product
    product.price = new_price

    return True