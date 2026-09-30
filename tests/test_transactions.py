from tests.conftest import register_and_login


def create_sample_transaction(client, headers):
    response = client.post(
        "/transactions",
        json={
            "title": "Lunch",
            "amount": 500,
            "type": "expense",
            "category": "Food",
            "date": "2026-09-29",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_get_transactions(client):
    headers = register_and_login(client)
    create_sample_transaction(client, headers)

    response = client.get("/transactions", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Food"


def test_get_specific_transaction(client):
    headers = register_and_login(client)
    transaction = create_sample_transaction(client, headers)

    response = client.get(f"/transactions/{transaction['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == transaction["id"]


def test_create_transaction(client):
    headers = register_and_login(client)
    response = client.post(
        "/transactions",
        json={
            "title": "Salary",
            "amount": 30000,
            "type": "income",
            "category": "Salary",
            "date": "2026-09-29",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["owner_id"] == 1
    assert response.json()["amount"] == 30000


def test_update_transaction(client):
    headers = register_and_login(client)
    transaction = create_sample_transaction(client, headers)

    response = client.put(
        f"/transactions/{transaction['id']}",
        json={"amount": 750, "category": "Groceries"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 750
    assert response.json()["category"] == "Groceries"


def test_delete_transaction(client):
    headers = register_and_login(client)
    transaction = create_sample_transaction(client, headers)

    response = client.delete(
        f"/transactions/{transaction['id']}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Transaction deleted successfully"

    get_response = client.get(
        f"/transactions/{transaction['id']}", headers=headers
    )
    assert get_response.status_code == 404
