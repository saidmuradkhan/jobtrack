import pytest

from preview import gate


@pytest.fixture
def gate_on(monkeypatch, settings):
    monkeypatch.setenv("PREVIEW_USER", "reviewer")
    monkeypatch.setenv("PREVIEW_PASSWORD", "long-test-password")
    monkeypatch.setenv("PREVIEW_SECRET", "shared-secret")
    settings.FRONTEND_URL = "https://jobs.example.dev"
    settings.PREVIEW_COOKIE_DOMAIN = ".example.dev"


def log_in(client, password="long-test-password", next_url="/admin/"):
    return client.post(
        "/preview/login", {"user": "reviewer", "password": password, "next": next_url}
    )


@pytest.mark.django_db
def test_site_is_open_without_preview_settings(client, monkeypatch):
    monkeypatch.delenv("PREVIEW_USER", raising=False)
    assert client.get("/api/applications/").status_code == 401  # JWT, not the gate
    assert "preview_login" not in client.get("/api/applications/").json()


@pytest.mark.django_db
def test_api_asks_for_the_preview_login(client, gate_on):
    response = client.get("/api/applications/")
    assert response.status_code == 401
    assert response.json()["preview_login"] == "http://testserver/preview/login"


@pytest.mark.django_db
def test_browser_is_sent_to_the_login_page(client, gate_on):
    response = client.get("/admin/", HTTP_ACCEPT="text/html")
    assert response.status_code == 302
    assert response["Location"] == "http://testserver/preview/login?next=%2Fadmin%2F"


@pytest.mark.django_db
def test_health_and_login_page_stay_open(client, gate_on):
    assert client.get("/health").status_code == 200
    page = client.get("/preview/login")
    assert page.status_code == 200
    assert b"This preview is private" in page.content


@pytest.mark.django_db
def test_wrong_password(client, gate_on):
    response = log_in(client, password="nope")
    assert response.status_code == 401
    assert gate.COOKIE_NAME not in response.cookies


@pytest.mark.django_db
def test_login_sets_a_cookie_for_every_subdomain(client, gate_on):
    response = log_in(client)

    assert response.status_code == 302
    assert response["Location"] == "/admin/"
    cookie = response.cookies[gate.COOKIE_NAME]
    assert cookie["domain"] == ".example.dev"
    assert cookie["httponly"]
    assert cookie["samesite"] == "Lax"


@pytest.mark.django_db
def test_cookie_opens_the_api(client, gate_on):
    log_in(client)
    response = client.get("/api/applications/")
    assert response.status_code == 401
    assert "preview_login" not in response.json()


@pytest.mark.django_db
def test_forged_cookie_is_refused(client, gate_on):
    client.cookies[gate.COOKIE_NAME] = "reviewer:forged:signature"
    assert "preview_login" in client.get("/api/applications/").json()


@pytest.mark.django_db
def test_services_pass_with_the_shared_token(client, gate_on):
    response = client.get("/api/applications/", HTTP_X_PREVIEW_TOKEN="shared-secret")
    assert "preview_login" not in response.json()
    response = client.get("/api/applications/", HTTP_X_PREVIEW_TOKEN="wrong")
    assert "preview_login" in response.json()


@pytest.mark.django_db
def test_cors_preflight_is_not_blocked(client, gate_on):
    response = client.options("/api/applications/")
    assert "preview_login" not in response.json()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("/admin/", "/admin/"),
        ("https://jobs.example.dev/", "https://jobs.example.dev/"),
        ("https://jobs.example.dev", "https://jobs.example.dev"),
        ("https://jobs.example.dev.evil.com/", "/health"),
        ("//evil.com", "/health"),
        ("https://evil.com", "/health"),
        (None, "/health"),
    ],
)
def test_safe_next(value, expected, settings):
    settings.FRONTEND_URL = "https://jobs.example.dev"
    assert gate.safe_next(value) == expected
