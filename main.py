from itertools import product

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ProductDB, PriceHistoryDB
from decimal import Decimal


app = FastAPI(title="StockWatch API")


#Defines what information a product contains
class ProductCreate(BaseModel):
    name : str
    price : float = Field(gt=0)
    quantity : int = Field(ge=0)
    product_url: str | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products")
def get_product(db: Session = Depends(get_db)):
    products = db.query(ProductDB).all()
    return products

@app.post("/products", status_code=201)
def create_product(
        product: ProductCreate,
        db: Session = Depends(get_db)
):
    new_product = ProductDB(
        **product.model_dump()
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/products/{product_id}")
def update_product(
        product_id: int,
        updated_product: ProductCreate,
        db: Session = Depends(get_db)
):
    # Step 1: Find the product
    product = db.get(ProductDB, product_id)

    if product is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )
    # Step 2: Compare prices
    old_price = Decimal(str(product.price))
    new_price = Decimal(str(updated_product.price))

    # Step 3: Save history if price changed
    if old_price != new_price:

        # Check whether history already exists
        existing_history = db.query(PriceHistoryDB).filter(
            PriceHistoryDB.product_id == product.id
        ).first()

        # Save the original price only once
        if existing_history is None:
            db.add(
                PriceHistoryDB(
                    product_id = product.id,
                    price = old_price
                )
            )
        #save the updated price
        db.add(
            PriceHistoryDB(
                product_id = product_id,
                price = new_price
            )
        )

    # Step 4: Update product information
    product.name = updated_product.name
    product.price = new_price
    product.quantity = updated_product.quantity
    product.product_url = updated_product.product_url

    # Step 5: Commit changes
    db.commit()
    db.refresh(product)

    return product

@app.get("/products/{product_id}/history")
def get_price_history(
        product_id: int,
        db: Session = Depends(get_db)
):
    # Step 1: Check whether the product exists
    product = db.get(ProductDB, product_id)

    if product is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )

    # Step 2: Retrieve the product's price history
    history = (
        db.query(PriceHistoryDB)
        .filter(PriceHistoryDB.product_id == product.id)
        .order_by(
            PriceHistoryDB.recorded_at.asc(),
            PriceHistoryDB.id.asc()
        )
        .all()
    )

    # Step 3: Return the records
    return history


@app.delete("/products/{product_id}",status_code=204)
def delete_product(
        product_id: int,
        db: Session = Depends(get_db)
):
    product = db.get(ProductDB, product_id)

    if product is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )

    db.delete(product)
    db.commit()