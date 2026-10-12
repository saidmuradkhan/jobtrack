import pytest


@pytest.mark.django_db
def test_admin_styles_are_served_without_collectstatic(client, monkeypatch):
    monkeypatch.setenv("PREVIEW_USER", "reviewer")
    monkeypatch.setenv("PREVIEW_PASSWORD", "long-test-password")
    response = client.get("/static/admin/css/base.css")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/css")
