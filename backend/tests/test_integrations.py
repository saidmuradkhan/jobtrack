import json
from pathlib import Path

import pytest
from django.core.cache import cache

from applications.models import Application
from integrations import views
from integrations.clients import ServiceUnavailable

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def services(monkeypatch):
    calls = []

    def fake_get_json(base_url, path, params=None):
        calls.append((base_url, path, params))
        if path == "/vacancies":
            return fixture("radar_vacancies.json")
        if path == "/rates":
            return fixture("cbar_rates.json")
        raise AssertionError(path)

    monkeypatch.setattr(views, "get_json", fake_get_json)
    cache.clear()
    return calls


@pytest.fixture
def services_down(monkeypatch):
    def fail(*args, **kwargs):
        raise ServiceUnavailable("connection refused")

    monkeypatch.setattr(views, "get_json", fail)
    cache.clear()


@pytest.mark.django_db
def test_vacancies_need_login(client, services):
    assert client.get("/api/vacancies/").status_code == 401
    assert client.get("/api/rates/").status_code == 401


@pytest.mark.django_db
def test_vacancies_come_from_radar(auth_client, services):
    response = auth_client.get("/api/vacancies/?q=python&category=it&page=2")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert body["categories"] == [["it", 2]]
    first = body["items"][0]
    assert first["uid"] == "boss.az:301245"
    assert first["salary_max"] == 3000.0
    assert first["saved"] is False
    assert "also_on" not in first

    _, path, params = services[0]
    assert path == "/vacancies"
    assert params == {"q": "python", "page": "2", "per_page": 20, "category": "it"}


@pytest.mark.django_db
def test_vacancies_marks_the_ones_already_saved(auth_client, user, other_user, services):
    Application.objects.create(
        user=user, company="Kapital Bank", position="Python developer", vacancy_uid="boss.az:301245"
    )
    Application.objects.create(
        user=other_user, company="Azercell", position="Frontend", vacancy_uid="jobsearch.az:88812"
    )

    items = auth_client.get("/api/vacancies/").json()["items"]

    assert [item["saved"] for item in items] == [True, False]


@pytest.mark.django_db
def test_vacancies_rejects_a_bad_page(auth_client, services):
    assert auth_client.get("/api/vacancies/?page=0").status_code == 400
    assert auth_client.get("/api/vacancies/?page=abc").status_code == 400


@pytest.mark.django_db
def test_vacancies_when_radar_is_down(auth_client, services_down):
    response = auth_client.get("/api/vacancies/")
    assert response.status_code == 502
    assert response.json()["detail"] == "Vacancies are unavailable right now."


@pytest.mark.django_db
def test_rates_per_unit_in_azn(auth_client, services):
    response = auth_client.get("/api/rates/")

    assert response.status_code == 200
    assert response.json() == {
        "date": "2026-10-08",
        "per_unit": {"EUR": 1.9048, "GBP": 2.2455, "TRY": 0.0398, "USD": 1.7},
    }


@pytest.mark.django_db
def test_rates_are_cached(auth_client, services):
    auth_client.get("/api/rates/")
    auth_client.get("/api/rates/")
    assert len(services) == 1


@pytest.mark.django_db
def test_rates_when_cbar_rates_is_down(auth_client, services_down):
    assert auth_client.get("/api/rates/").status_code == 502
