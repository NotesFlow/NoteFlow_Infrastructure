def test_register_login_and_me_flow(client):
    register_response = client.post(
        "/register",
        json={
            "username": "albert",
            "email": "albert@example.com",
            "password": "parola123",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["username"] == "albert"
    assert register_response.json()["email"] == "albert@example.com"

    login_response = client.post(
        "/login",
        json={
            "username": "albert",
            "password": "parola123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token
    assert login_response.json()["token_type"] == "bearer"

    me_response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["username"] == "albert"
    assert me_response.json()["email"] == "albert@example.com"


def test_register_rejects_duplicate_username_or_email(client):
    payload = {
        "username": "albert",
        "email": "albert@example.com",
        "password": "parola123",
    }

    first_response = client.post("/register", json=payload)
    second_response = client.post("/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username or email already exists"


def test_login_rejects_invalid_credentials(client):
    client.post(
        "/register",
        json={
            "username": "albert",
            "email": "albert@example.com",
            "password": "parola123",
        },
    )

    response = client.post(
        "/login",
        json={
            "username": "albert",
            "password": "gresita123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_me_requires_valid_token(client):
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
