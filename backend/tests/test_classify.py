from pathlib import Path

import pytest

from inbox.classify import (
    JobEmail,
    classify,
    company_from_sender,
    company_key,
    forwarding_confirmation,
)
from inbox.reading import Email, read_email

FIXTURES = Path(__file__).parent / "fixtures" / "emails"


def load(name):
    return read_email((FIXTURES / name).read_bytes())


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("linkedin_applied.eml", JobEmail("applied", "Acme Bank", "Backend Developer")),
        ("greenhouse_received.eml", JobEmail("applied", "Northwind", "Senior Python Engineer")),
        ("interview_az.eml", JobEmail("interview", "Acme Bank", "Backend Developer")),
        ("rejection.eml", JobEmail("rejected", "Northwind", "Senior Python Engineer")),
        ("offer.eml", JobEmail("offer", "Contoso", "Data Engineer")),
    ],
)
def test_classifies_job_emails(fixture, expected):
    assert classify(load(fixture)) == expected


def test_ignores_emails_that_are_not_about_a_job():
    assert classify(load("newsletter.eml")) == JobEmail(status=None)


def test_subject_wins_over_a_maybe_in_the_text():
    email = Email(
        sender_name="Fabrikam Careers",
        sender_address="jobs@fabrikam.example",
        subject="Thank you for applying",
        text="If your profile matches, we will invite you to an interview.",
    )
    assert classify(email).status == "applied"


def test_rejection_wins_over_interview_in_the_same_text():
    email = Email(
        sender_name="",
        sender_address="hr@fabrikam.example",
        subject="Your application",
        text="Thank you for the interview. Unfortunately we chose another candidate.",
    )
    assert classify(email) == JobEmail("rejected", "Fabrikam", "")


@pytest.mark.parametrize(
    ("name", "address", "company"),
    [
        ("Acme Bank HR", "hr@acmebank.az", "Acme Bank"),
        ("Northwind via Greenhouse", "no-reply@greenhouse.io", "Northwind"),
        ("LinkedIn", "jobs-noreply@linkedin.com", ""),
        ("", "careers@fabrikam.example", "Fabrikam"),
        ("", "someone@gmail.com", ""),
    ],
)
def test_company_from_sender(name, address, company):
    email = Email(sender_name=name, sender_address=address, subject="", text="")
    assert company_from_sender(email) == company


def test_reads_the_gmail_forwarding_code():
    found = forwarding_confirmation(load("gmail_forwarding.eml"))
    assert found["code"] == "482913775"
    assert found["link"].startswith("https://mail-settings.google.com/mail/vf-")
    assert forwarding_confirmation(load("offer.eml")) is None


def test_company_key_ignores_case_spaces_and_legal_form():
    assert company_key("Acme Bank LLC") == company_key("ACME BANK") == "acmebank"
    assert company_key("Kapital Bank ASC") == "kapitalbank"
