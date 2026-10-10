from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone

from applications.models import Application
from inbox.models import InboundEmail
from inbox.processing import process_email
from inbox.reading import read_email

URL = "/api/inbox/"
FIXTURES = Path(__file__).parent / "fixtures" / "emails"


def receive(user, fixture):
    return process_email(user, read_email((FIXTURES / fixture).read_bytes()))


@pytest.mark.django_db
def test_inbox_lists_recent_emails_without_forwarding_codes(auth_client, user):
    receive(user, "linkedin_applied.eml")
    receive(user, "offer.eml")
    receive(user, "gmail_forwarding.eml")
    body = auth_client.get(URL).json()
    assert body["pending"] == 1
    assert [email["outcome"] for email in body["emails"]] == ["pending", "created"]
    created = body["emails"][1]
    assert created["application"]["company"] == "Acme Bank"
    assert body["forwarding_confirmation"]["forwarding_code"] == "482913775"


@pytest.mark.django_db
def test_old_forwarding_codes_are_hidden(auth_client, user):
    record = receive(user, "gmail_forwarding.eml")
    InboundEmail.objects.filter(pk=record.pk).update(received_at=timezone.now() - timedelta(days=8))
    assert auth_client.get(URL).json()["forwarding_confirmation"] is None


@pytest.mark.django_db
def test_inbox_shows_only_own_emails(auth_client, other_user):
    receive(other_user, "linkedin_applied.eml")
    assert auth_client.get(URL).json()["emails"] == []


@pytest.mark.django_db
def test_accept_creates_the_application(auth_client, user):
    record = receive(user, "offer.eml")
    response = auth_client.post(f"{URL}emails/{record.pk}/accept/")
    assert response.status_code == 200
    assert response.json()["outcome"] == "created"
    app = Application.objects.get(user=user)
    assert (app.company, app.position, app.status) == ("Contoso", "Data Engineer", "offer")


@pytest.mark.django_db
def test_accept_updates_the_chosen_application(auth_client, user):
    app = Application.objects.create(user=user, company="Contoso Group", position="Data Engineer")
    record = receive(user, "offer.eml")
    response = auth_client.post(
        f"{URL}emails/{record.pk}/accept/", {"application": app.pk}, format="json"
    )
    app.refresh_from_db()
    assert response.json()["previous_status"] == "applied"
    assert app.status == "offer"


@pytest.mark.django_db
def test_accept_cannot_use_someone_elses_application(auth_client, user, other_user):
    theirs = Application.objects.create(user=other_user, company="Contoso", position="X")
    record = receive(user, "offer.eml")
    response = auth_client.post(
        f"{URL}emails/{record.pk}/accept/", {"application": theirs.pk}, format="json"
    )
    assert response.status_code == 404
    theirs.refresh_from_db()
    assert theirs.status == "applied"


@pytest.mark.django_db
def test_accept_without_company_needs_an_application(auth_client, user):
    record = InboundEmail.objects.create(
        user=user, sender="no-reply@lever.co", status="applied", outcome="pending"
    )
    response = auth_client.post(f"{URL}emails/{record.pk}/accept/")
    assert response.status_code == 400


@pytest.mark.django_db
def test_dismiss_and_only_pending_can_be_answered(auth_client, user, other_user):
    record = receive(user, "offer.eml")
    assert auth_client.post(f"{URL}emails/{record.pk}/dismiss/").json()["outcome"] == "dismissed"
    assert auth_client.post(f"{URL}emails/{record.pk}/accept/").status_code == 404

    theirs = receive(other_user, "offer.eml")
    assert auth_client.post(f"{URL}emails/{theirs.pk}/dismiss/").status_code == 404
