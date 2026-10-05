import pytest
from django.contrib.auth.models import User

PASSWORD = "s3cure-pass-123"


@pytest.mark.django_db
def test_register_creates_user(client):
    response = client.post(
        "/api/auth/register/",
        {"username": "newbie", "email": "new@example.com", "password": PASSWORD},
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": response.json()["id"],
        "username": "newbie",
        "email": "new@example.com",
    }
    assert User.objects.get(username="newbie").check_password(PASSWORD)


@pytest.mark.django_db
def test_register_rejects_weak_password(client):
    response = client.post("/api/auth/register/", {"username": "newbie", "password": "12345"})
    assert response.status_code == 400
    assert "password" in response.json()
    assert not User.objects.filter(username="newbie").exists()


@pytest.mark.django_db
def test_register_rejects_taken_username(client, user):
    response = client.post("/api/auth/register/", {"username": user.username, "password": PASSWORD})
    assert response.status_code == 400
    assert "username" in response.json()


@pytest.mark.django_db
def test_login_refresh_and_me(client, user):
    tokens = client.post("/api/auth/token/", {"username": "said", "password": PASSWORD}).json()
    assert {"access", "refresh"} <= tokens.keys()

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    assert client.get("/api/auth/me/").json()["username"] == "said"

    refreshed = client.post("/api/auth/token/refresh/", {"refresh": tokens["refresh"]})
    assert refreshed.status_code == 200
    assert "access" in refreshed.json()


@pytest.mark.django_db
def test_wrong_password_gets_no_token(client, user):
    response = client.post("/api/auth/token/", {"username": "said", "password": "nope"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_requires_login(client):
    assert client.get("/api/auth/me/").status_code == 401
