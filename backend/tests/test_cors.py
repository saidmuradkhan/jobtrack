import pytest

FRONTEND = "https://jobs.example.dev"


@pytest.fixture
def frontend(settings):
    settings.FRONTEND_URL = FRONTEND
    settings.CORS_ALLOWED_ORIGINS = [FRONTEND]


@pytest.mark.django_db
def test_preflight_from_the_frontend_is_allowed(client, frontend):
    response = client.options(
        "/api/applications/",
        HTTP_ORIGIN=FRONTEND,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization, content-type",
    )
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == FRONTEND
    assert response["Access-Control-Allow-Credentials"] == "true"
    assert "authorization" in response["Access-Control-Allow-Headers"]


@pytest.mark.django_db
def test_other_sites_get_no_cors_headers(client, frontend):
    response = client.get("/api/applications/", HTTP_ORIGIN="https://evil.example.com")
    assert "Access-Control-Allow-Origin" not in response


@pytest.mark.django_db
def test_preview_login_answer_is_readable_by_the_frontend(client, frontend, monkeypatch):
    monkeypatch.setenv("PREVIEW_USER", "reviewer")
    monkeypatch.setenv("PREVIEW_PASSWORD", "long-test-password")
    response = client.get("/api/applications/", HTTP_ORIGIN=FRONTEND)
    assert response.status_code == 401
    assert "preview_login" in response.json()
    assert response["Access-Control-Allow-Origin"] == FRONTEND
