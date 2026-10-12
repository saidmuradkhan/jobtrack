from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command

from applications.models import Application
from inbox.models import InboundEmail


def seed(**options):
    out = StringIO()
    call_command("seed_demo", stdout=out, **options)
    return out.getvalue()


@pytest.mark.django_db
def test_creates_a_demo_user_with_a_random_password(monkeypatch):
    monkeypatch.delenv("DEMO_PASSWORD", raising=False)
    out = seed()

    demo = User.objects.get(username="demo")
    password = out.split("Password: ")[1].strip()
    assert demo.check_password(password)
    assert demo.applications.count() == 12
    assert set(demo.applications.values_list("status", flat=True)) == set(Application.Status)
    assert demo.inbox.address.startswith("jobs+demo-")


@pytest.mark.django_db
def test_email_updates_point_at_the_seeded_applications():
    seed(password="demo-pass-123")
    emails = InboundEmail.objects.filter(user__username="demo")

    assert emails.count() == 4
    updated = emails.get(outcome=InboundEmail.Outcome.UPDATED, company="Caspian Digital")
    assert updated.application.status == Application.Status.INTERVIEW
    pending = emails.get(outcome=InboundEmail.Outcome.PENDING)
    assert pending.application is None


@pytest.mark.django_db
def test_password_can_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", "from-env-pass-123")
    out = seed(username="reviewer")
    assert "Password" not in out
    assert User.objects.get(username="reviewer").check_password("from-env-pass-123")


@pytest.mark.django_db
def test_keeps_real_data_unless_asked_to_reset(user):
    Application.objects.create(user=user, company="Real Co", position="Developer")

    with pytest.raises(CommandError):
        seed(username="said")
    assert user.applications.get().company == "Real Co"

    seed(username="said", reset=True)
    assert user.applications.count() == 12
    assert not user.applications.filter(company="Real Co").exists()
    user.refresh_from_db()
    assert user.check_password("s3cure-pass-123")


@pytest.mark.django_db
def test_running_twice_with_reset_does_not_duplicate():
    seed(password="demo-pass-123")
    seed(reset=True)
    assert Application.objects.filter(user__username="demo").count() == 12
    assert InboundEmail.objects.filter(user__username="demo").count() == 4
