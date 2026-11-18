import pytest
from decimal import Decimal

from conftest import TestingSessionLocal
from models import ProductDB
from services.price_checker import check_product_price

def test_check_product_price_changed(client):
    # Step 1: Create a product through the API
    response = client.post(
        "/products",
        json={
            "name": "ASUS Monitor",
            "price": 249.99,
            "quantity": 5,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    # Step 2: Check the product price
    with TestingSessionLocal() as db:
        result = check_product_price(db, product_id)

    # Step 3: Verify the comparison
    assert result["product_id"] == product_id
    assert result["price_changed"] is True
    assert result["old_price"] == Decimal("249.99")
    assert result["new_price"] == Decimal("199.99")

    # Step 4: Verify the new price was saved in PostgreSQL
    with TestingSessionLocal() as db:
        updated_product = db.get(ProductDB, product_id)

        assert updated_product is not None

        assert Decimal(str(updated_product.price)) == Decimal("199.99")

    # Step 5: Verify price history was saved
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2

    prices = [
        Decimal(str(item["price"]))
        for item in history
    ]

    assert prices == [
        Decimal("249.99"),
        Decimal("199.99")
    ]


def test_check_product_price_unchanged(client):
    response = client.post(
        "/products",
        json={
            "name": "ASUS Monitor",
            "price": 199.99,
            "quantity": 5,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    with TestingSessionLocal() as db:
        result = check_product_price(db, product_id)

        assert result["product_id"] == product_id
        assert result["price_changed"] is False
        assert result["current_price"] == Decimal("199.99")


def test_check_product_price_not_found(client):
    with TestingSessionLocal() as db:
        with pytest.raises(
            ValueError,
            match="Product not found"
        ):
            check_product_price(db, 999999)


def test_repeated_price_checks_do_not_duplicate_history(client):
    # Step 1: Create a product with a higher price
    response = client.post(
        "/products",
        json={
            "name": "ASUS Monitor",
            "price": 249.99,
            "quantity": 5,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    # Step 2: Run the price checker three times
    with TestingSessionLocal() as db:
        first_check = check_product_price(db, product_id)
        second_check = check_product_price(db, product_id)
        third_check = check_product_price(db, product_id)

    # Step 3: Verify only the first check detected a change
    assert first_check["price_changed"] is True
    assert second_check["price_changed"] is False
    assert third_check["price_changed"] is False

    # Step 4: Verify the database contains only two history records
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2

    prices = [
        Decimal(str(item["price"]))
        for item in history
    ]

    assert prices == [
        Decimal("249.99"),
        Decimal("199.99")
    ]

