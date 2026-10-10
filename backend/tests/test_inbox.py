from pathlib import Path

import pytest

from applications.models import Application
from inbox.models import InboundEmail, Inbox

URL = "/api/inbox/"


@pytest.mark.django_db
def test_inbox_requires_login(client):
    assert client.get(URL).status_code == 401


@pytest.mark.django_db
def test_each_user_gets_one_private_address(auth_client, user, settings):
    settings.INBOX_DOMAIN = "in.example.test"
    first = auth_client.get(URL).json()["address"]
    second = auth_client.get(URL).json()["address"]
    assert first == second
    assert first.startswith("said-")
    assert first.endswith("@in.example.test")
    assert Inbox.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_addresses_are_hard_to_guess(user, other_user):
    mine = Inbox.objects.create(user=user)
    theirs = Inbox.objects.create(user=other_user)
    assert mine.key != theirs.key
    assert len(mine.key) == 10


@pytest.mark.django_db
def test_address_keeps_only_safe_characters(django_user_model, settings):
    settings.INBOX_DOMAIN = "in.example.test"
    odd = django_user_model.objects.create_user(username="Said.M+jobs@home", password="x")
    box = Inbox.objects.create(user=odd, key="abc123")
    assert box.address == "saidmjobshome-abc123@in.example.test"


RECEIVE = "/api/inbox/receive/"
FIXTURES = Path(__file__).parent / "fixtures" / "emails"


def post_email(client, fixture, to, secret="hook-secret"):
    return client.generic(
        "POST",
        RECEIVE,
        (FIXTURES / fixture).read_bytes(),
        content_type="message/rfc822",
        headers={"X-Inbox-Secret": secret, "X-Inbox-To": to},
    )


@pytest.fixture
def webhook(settings):
    settings.INBOX_WEBHOOK_SECRET = "hook-secret"


@pytest.mark.django_db
def test_forwarded_email_reaches_its_owner(client, user, webhook):
    box = Inbox.objects.create(user=user, key="ab12cd34ef")
    response = post_email(client, "linkedin_applied.eml", to=box.address.upper())
    assert response.status_code == 200
    assert response.json() == {"outcome": "created"}
    assert Application.objects.get().user == user


@pytest.mark.django_db
def test_webhook_needs_the_secret(client, user, webhook):
    box = Inbox.objects.create(user=user)
    assert post_email(client, "offer.eml", box.address, secret="nope").status_code == 403
    assert not InboundEmail.objects.exists()


@pytest.mark.django_db
def test_webhook_is_off_without_a_secret(client, user):
    box = Inbox.objects.create(user=user)
    assert post_email(client, "offer.eml", box.address, secret="").status_code == 503


@pytest.mark.django_db
def test_unknown_address_is_refused(client, webhook):
    assert post_email(client, "offer.eml", "said-0000000000@in.example").status_code == 404


@pytest.mark.django_db
def test_webhook_only_takes_post(client, webhook):
    assert client.get(RECEIVE).status_code == 405


@pytest.mark.django_db
def test_webhook_passes_the_preview_gate(client, user, webhook, monkeypatch):
    monkeypatch.setenv("PREVIEW_USER", "reviewer")
    monkeypatch.setenv("PREVIEW_PASSWORD", "letmein")
    box = Inbox.objects.create(user=user)
    assert post_email(client, "offer.eml", box.address).status_code == 200
    assert client.get(URL).status_code == 401
