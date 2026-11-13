from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ProductDB


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
    product = db.get(ProductDB, product_id)

    if product is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )

    product.name = updated_product.name
    product.price = updated_product.price
    product.quantity = updated_product.quantity
    product.product_url = updated_product.product_url

    db.commit()
    db.refresh(product)

    return product




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