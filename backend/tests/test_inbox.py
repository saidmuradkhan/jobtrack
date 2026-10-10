import pytest

from inbox.models import Inbox

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
