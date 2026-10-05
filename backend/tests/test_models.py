from datetime import date

import pytest
from django.contrib import admin
from django.utils import timezone

from applications.models import Application


@pytest.mark.django_db
def test_defaults(user):
    app = Application.objects.create(user=user, company="Leops", position="Backend Developer")
    assert app.status == Application.Status.APPLIED
    assert app.currency == "AZN"
    assert app.applied_on == timezone.localdate()
    assert str(app) == "Backend Developer at Leops"


@pytest.mark.django_db
def test_newest_applications_come_first(user):
    Application.objects.create(user=user, company="A", position="Dev", applied_on=date(2026, 9, 1))
    Application.objects.create(user=user, company="B", position="Dev", applied_on=date(2026, 10, 1))
    assert [a.company for a in Application.objects.all()] == ["B", "A"]


@pytest.mark.django_db
def test_deleting_user_removes_their_applications(user):
    Application.objects.create(user=user, company="Leops", position="Dev")
    user.delete()
    assert Application.objects.count() == 0


def test_registered_in_admin():
    assert admin.site.is_registered(Application)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
