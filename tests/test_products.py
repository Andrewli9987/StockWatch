def test_create_product(client):
    response = client.post(
        "/products",
        json={
            "name": "Test Monitor",
            "price": 199.99,
            "quantity": 5,
            "product_url": "https://example.com/monitor"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Monitor"
    assert float(data["price"]) == 199.99
    assert data["quantity"] == 5
    assert data["product_url"] == "https://example.com/monitor"
    assert isinstance(data["id"], int)

def test_create_product_negative_price(client):
    response = client.post(
        "/products",
        json={
            "name": "Invalid Monitor",
            "price": -50,
            "quantity": 5,
        }
    )

    assert response.status_code == 422

def test_create_product_negative_quantity(client):
    response = client.post(
        "/products",
        json={
            "name": "Invalid Keyboard",
            "price": 99.99,
            "quantity": -3,
        }
    )

    assert response.status_code == 422

def test_get_products(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_product(client):
    create_response = client.post(
        "/products",
        json={
            "name": "Gaming Mouse",
            "price": "59.99",
            "quantity": 10
        }
    )

    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    update_response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Gaming Mouse",
            "price": "49.99",
            "quantity": 15
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["name"] == "Updated Gaming Mouse"
    assert float(data["price"]) == 49.99
    assert data["quantity"] == 15


def test_delete_product(client):
    create_response = client.post(
        "/products",
        json={
            "name": "Test Keyboard",
            "price": "89.99",
            "quantity": 5
        }
    )

    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/products/{product_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get("/products")

    assert all(
        product["id"] != product_id
        for product in get_response.json()
    )

def test_update_nonexistent_product(client):
    response = client.put(
        "/products/99999",
        json={
            "name": "Unknown Product",
            "price": 49.99,
            "quantity": 5
        }
    )

    assert response.status_code == 404

def test_delete_nonexistent_product(client):
    response = client.delete("/products/99999")

    assert response.status_code == 404