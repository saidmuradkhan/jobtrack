from datetime import date

import pytest

from applications.models import Application

URL = "/api/applications/"


def make(user, **fields):
    data = {"company": "Leops", "position": "Backend Developer"} | fields
    return Application.objects.create(user=user, **data)


@pytest.mark.django_db
def test_requires_login(client):
    assert client.get(URL).status_code == 401


@pytest.mark.django_db
def test_create_sets_owner(auth_client, user):
    response = auth_client.post(
        URL,
        {
            "company": "Kapital Bank",
            "position": "Python Developer",
            "salary": 2500,
            "currency": "usd",
            "url": "https://boss.az/vacancies/1",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "applied"
    assert body["currency"] == "USD"
    assert Application.objects.get(pk=body["id"]).user == user


@pytest.mark.django_db
def test_list_shows_only_own_applications(auth_client, user, other_user):
    make(user, company="Mine")
    make(other_user, company="Theirs")
    companies = [item["company"] for item in auth_client.get(URL).json()]
    assert companies == ["Mine"]


@pytest.mark.django_db
def test_cannot_touch_someone_elses_application(auth_client, other_user):
    theirs = make(other_user)
    detail = f"{URL}{theirs.pk}/"
    assert auth_client.get(detail).status_code == 404
    assert auth_client.patch(detail, {"status": "offer"}).status_code == 404
    assert auth_client.delete(detail).status_code == 404
    assert Application.objects.filter(pk=theirs.pk).exists()


@pytest.mark.django_db
def test_update_and_delete(auth_client, user):
    app = make(user)
    detail = f"{URL}{app.pk}/"

    response = auth_client.patch(detail, {"status": "interview", "notes": "Call on Monday"})
    assert response.status_code == 200
    app.refresh_from_db()
    assert app.status == "interview"
    assert app.notes == "Call on Monday"

    assert auth_client.delete(detail).status_code == 204
    assert not Application.objects.filter(pk=app.pk).exists()


@pytest.mark.django_db
def test_filter_by_status(auth_client, user):
    make(user, company="A", status="applied")
    make(user, company="B", status="offer")
    companies = [item["company"] for item in auth_client.get(URL, {"status": "offer"}).json()]
    assert companies == ["B"]


@pytest.mark.django_db
def test_search_and_ordering(auth_client, user):
    make(user, company="Leops", position="React Developer", applied_on=date(2026, 9, 1))
    make(user, company="Azercell", position="Python Developer", applied_on=date(2026, 10, 1))
    make(user, company="Pasha Bank", position="Python Engineer", applied_on=date(2026, 8, 1))

    found = auth_client.get(URL, {"search": "python"}).json()
    assert [item["company"] for item in found] == ["Azercell", "Pasha Bank"]

    by_company = auth_client.get(URL, {"ordering": "company"}).json()
    assert [item["company"] for item in by_company] == ["Azercell", "Leops", "Pasha Bank"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fields",
    [
        {"company": ""},
        {"status": "ghosted"},
        {"salary": -100},
        {"currency": "MANAT"},
        {"url": "not a link"},
    ],
)
def test_validation(auth_client, fields):
    data = {"company": "Leops", "position": "Dev"} | fields
    response = auth_client.post(URL, data)
    assert response.status_code == 400
    assert next(iter(fields)) in response.json()


@pytest.mark.django_db
def test_user_field_cannot_be_forged(auth_client, user, other_user):
    response = auth_client.post(URL, {"company": "X", "position": "Y", "user": other_user.pk})
    assert response.status_code == 201
    assert Application.objects.get(pk=response.json()["id"]).user == user


@pytest.mark.django_db
def test_vacancy_can_be_saved_only_once(auth_client):
    data = {"company": "Kapital Bank", "position": "QA Engineer", "vacancy_uid": "boss.az:123"}
    assert auth_client.post(URL, data).status_code == 201

    response = auth_client.post(URL, data)
    assert response.status_code == 400
    assert response.json()["vacancy_uid"] == ["You already saved this vacancy."]


@pytest.mark.django_db
def test_same_vacancy_for_two_users(auth_client, other_user):
    make(other_user, vacancy_uid="boss.az:123")
    response = auth_client.post(
        URL, {"company": "Kapital Bank", "position": "QA Engineer", "vacancy_uid": "boss.az:123"}
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_editing_a_saved_vacancy_keeps_its_uid(auth_client, user):
    application = make(user, vacancy_uid="boss.az:123")
    response = auth_client.patch(
        f"{URL}{application.pk}/", {"status": "interview", "vacancy_uid": "boss.az:123"}
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_many_applications_without_a_vacancy(auth_client):
    for _ in range(2):
        assert auth_client.post(URL, {"company": "Leops", "position": "Dev"}).status_code == 201
