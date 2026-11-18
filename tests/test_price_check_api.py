from decimal import Decimal


def test_check_price_endpoint(client):
    # Step 1: Create a product
    response = client.post(
        "/products",
        json={
            "name": "Samsung Monitor",
            "price": 299.99,
            "quantity": 5,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    # Step 2: Trigger the price check through FastAPI
    response = client.post(
        f"/products/{product_id}/check-price"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["price_changed"] is True
    assert Decimal(str(result["old_price"])) == Decimal("299.99")
    assert Decimal(str(result["new_price"])) == Decimal("199.99")

    # Step 3: Check the same product again
    response = client.post(
        f"/products/{product_id}/check-price"
    )

    assert response.status_code == 200
    assert response.json()["price_changed"] is False

    # Step 4: Verify the history
    response = client.get(
        f"/products/{product_id}/history"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_check_price_product_not_found(client):
    response = client.post(
        "/products/999999/check-price"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"



def test_check_price_missing_url(client):
    response = client.post(
        "/products",
        json={
            "name": "Logitech Mouse",
            "price": 69.99,
            "quantity": 10
        }
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    response = client.post(
        f"/products/{product_id}/check-price"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Product URL is missing"
