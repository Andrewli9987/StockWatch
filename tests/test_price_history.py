from models import PriceHistoryDB
from database import SessionLocal
from conftest import TestingSessionLocal


def test_price_change_creates_history(client):
    # Step 1: Create a product
    response = client.post(
        "/products",
        json={
            "name": "ASUS monitor",
            "price": 249.99,
            "quantity": 8,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 201


    product_id = response.json()["id"]

    # Step 2: Update the price
    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "ASUS monitor",
            "price": 199.99,
            "quantity": 8,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 200

    # Step 3: Retrieve price history
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200

    history = response.json()
    # Step 4: Verify both prices were recorded

    assert len(history) == 2
    assert float(history[0]["price"]) == 249.99
    assert float(history[1]["price"])== 199.99


def test_multiple_price_changes(client):
    # Create a product
    response = client.post(
        "/products",
        json={
            "name": "Razer Keyboard",
            "price": 150.00,
            "quantity": 5,
        }
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    # Update the price multiple times
    for price in [130.00, 110.00, 90.00]:
        response = client.put(
            f"/products/{product_id}",
            json={
                "name": "Razer Keyboard",
                "price": price,
                "quantity": 5,
            }
        )

        assert response.status_code == 200

    # Retrieve price history
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200
    history = response.json()

    # Verify all prices were recorded
    assert len(history) == 4

    prices = [
        float(record["price"])
        for record in history
    ]

    assert prices == [150.00, 130.00, 110.00, 90.00]

def test_unchanged_price_does_not_create_history(client):
    # Step 1: Create a product
    response = client.post(
        "/products",
        json={
            "name": "ASUS monitor",
            "price": 249.99,
            "quantity": 5,
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    #Step 2: Update quantity, but keep price unchanged
    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "ASUS monitor",
            "price": 249.99,
            "quantity": 10,
        }
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 10

    # Step 3: Retrieve price history
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200

    history = response.json()

    # Step 4: Verify no history was created
    assert len(history) == 0

def test_price_histor_product_not_found(client):
    # Step 1: Request history for a nonexistent product
    response = client.get(
        "/products/999999/history"
    )

    # Step 2: Verify the HTTP status code
    assert response.status_code ==  404

    # Step 3: Verify the error message
    assert response.json() == {
        "detail": "Product not found"
    }

def test_delete_product_with_price_history(client):
    # Step 1: Create a product
    response = client.post(
        "/products",
        json={
            "name": "ASUS monitor",
            "price": 249.99,
            "quantity": 8,
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    # Step 2: Change its price
    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "ASUS monitor",
            "price": 199.99,
            "quantity": 8,
        }
    )
    assert response.status_code == 200

    # Step 3: Verify history exists
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

    # Step 4: Delete the product
    response = client.delete(
        f"/products/{product_id}"
    )
    assert response.status_code == 204

    # Step 5: Verify the product no longer exists
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 404

    # Step 6: Verify PostgreSQL deleted the price history
    with TestingSessionLocal() as db:
        remaining_history = (
            db.query(PriceHistoryDB)
            .filter(PriceHistoryDB.product_id == product_id)
            .all()
        )

        assert len(remaining_history) == 0