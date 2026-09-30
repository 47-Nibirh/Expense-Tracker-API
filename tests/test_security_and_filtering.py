from tests.conftest import register_and_login


def test_registration_does_not_return_password(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "secureuser",
            "email": "secure@example.com",
            "password": "secret123",
        },
    )
    assert response.status_code == 201
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


def test_transaction_requires_authentication(client):
    response = client.get("/transactions")
    assert response.status_code == 401


def test_transaction_filter(client):
    headers = register_and_login(client)
    client.post(
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
    client.post(
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

    response = client.get(
        "/transactions/filter?type=expense&category=Food&minimum_amount=100&maximum_amount=5000",
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Lunch"


def test_user_cannot_access_another_users_transaction(client):
    alice_headers = register_and_login(client)
    client.post(
        "/auth/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "otherpass123",
        },
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "otheruser", "password": "otherpass123"},
    )
    other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    transaction = client.post(
        "/transactions",
        json={
            "title": "Private transaction",
            "amount": 100,
            "type": "expense",
            "category": "Private",
            "date": "2026-09-29",
        },
        headers=alice_headers,
    ).json()

    assert client.get(
        f"/transactions/{transaction['id']}", headers=other_headers
    ).status_code == 404
    assert client.put(
        f"/transactions/{transaction['id']}",
        json={"amount": 999},
        headers=other_headers,
    ).status_code == 404
    assert client.delete(
        f"/transactions/{transaction['id']}", headers=other_headers
    ).status_code == 404
