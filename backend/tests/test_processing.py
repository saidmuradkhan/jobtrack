from datetime import date
from pathlib import Path

import pytest

from applications.models import Application
from inbox.models import InboundEmail
from inbox.processing import process_email, status_change
from inbox.reading import Email, read_email

FIXTURES = Path(__file__).parent / "fixtures" / "emails"


def load(name):
    return read_email((FIXTURES / name).read_bytes())


def make(user, **fields):
    data = {"company": "Acme Bank", "position": "Backend Developer"} | fields
    return Application.objects.create(user=user, **data)


@pytest.mark.parametrize(
    ("current", "new", "change"),
    [
        ("wishlist", "applied", "move"),
        ("applied", "interview", "move"),
        ("interview", "offer", "move"),
        ("interview", "rejected", "move"),
        ("interview", "applied", "keep"),
        ("applied", "applied", "keep"),
        ("rejected", "interview", "ask"),
        ("offer", "rejected", "ask"),
    ],
)
def test_status_change(current, new, change):
    assert status_change(current, new) == change


@pytest.mark.django_db
def test_application_email_adds_a_new_application(user):
    record = process_email(user, load("linkedin_applied.eml"))
    assert record.outcome == "created"
    app = record.application
    assert (app.company, app.position, app.status) == ("Acme Bank", "Backend Developer", "applied")
    assert app.applied_on == date(2026, 10, 9)
    assert app.notes == "Added from an email: Said, your application was sent to Acme Bank"


@pytest.mark.django_db
def test_interview_email_moves_a_manually_added_application(user):
    app = make(user, company="ACME BANK LLC", status="applied")
    record = process_email(user, load("interview_az.eml"))
    app.refresh_from_db()
    assert record.outcome == "updated"
    assert record.previous_status == "applied"
    assert record.application == app
    assert app.status == "interview"


@pytest.mark.django_db
def test_late_confirmation_does_not_undo_progress(user):
    app = make(user, status="interview")
    record = process_email(user, load("linkedin_applied.eml"))
    app.refresh_from_db()
    assert record.outcome == "unchanged"
    assert app.status == "interview"


@pytest.mark.django_db
def test_status_email_for_an_unknown_company_waits_for_the_user(user):
    record = process_email(user, load("offer.eml"))
    assert record.outcome == "pending"
    assert record.application is None
    assert (record.status, record.company, record.position) == ("offer", "Contoso", "Data Engineer")
    assert not Application.objects.exists()


@pytest.mark.django_db
def test_two_applications_at_one_company_are_told_apart_by_position(user):
    make(user, company="Northwind", position="Data Analyst")
    engineer = make(
        user, company="Northwind", position="Senior Python Engineer", status="interview"
    )
    record = process_email(user, load("rejection.eml"))
    engineer.refresh_from_db()
    assert record.application == engineer
    assert engineer.status == "rejected"


@pytest.mark.django_db
def test_unclear_match_waits_for_the_user(user):
    make(user, company="Northwind", position="Data Analyst")
    make(user, company="Northwind", position="QA Engineer")
    assert process_email(user, load("rejection.eml")).outcome == "pending"


@pytest.mark.django_db
def test_only_the_owner_applications_are_touched(user, other_user):
    theirs = make(other_user, status="applied")
    record = process_email(user, load("interview_az.eml"))
    theirs.refresh_from_db()
    assert record.outcome == "pending"
    assert theirs.status == "applied"


@pytest.mark.django_db
def test_other_emails_are_ignored_without_keeping_the_text(user):
    record = process_email(user, load("newsletter.eml"))
    assert record.outcome == "ignored"
    assert record.snippet == ""
    assert not Application.objects.exists()


@pytest.mark.django_db
def test_gmail_forwarding_code_is_kept(user):
    record = process_email(user, load("gmail_forwarding.eml"))
    assert record.outcome == "forwarding"
    assert record.forwarding_code == "482913775"


@pytest.mark.django_db
def test_the_same_email_is_handled_once(user):
    first = process_email(user, load("linkedin_applied.eml"))
    second = process_email(user, load("linkedin_applied.eml"))
    assert first.pk == second.pk
    assert Application.objects.count() == 1
    assert InboundEmail.objects.count() == 1


@pytest.mark.django_db
def test_email_without_company_waits_for_the_user(user):
    email = Email(
        sender_name="",
        sender_address="no-reply@lever.co",
        subject="Thank you for applying",
        text="We received your application.",
    )
    record = process_email(user, email)
    assert record.outcome == "pending"
    assert record.company == ""
