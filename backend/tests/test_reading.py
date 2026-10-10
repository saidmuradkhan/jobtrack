from pathlib import Path

from inbox.reading import html_to_text, read_email

FIXTURES = Path(__file__).parent / "fixtures" / "emails"


def load(name):
    return read_email((FIXTURES / name).read_bytes())


def test_reads_sender_subject_and_text():
    email = load("linkedin_applied.eml")
    assert email.sender_name == "LinkedIn"
    assert email.sender_address == "jobs-noreply@linkedin.com"
    assert email.subject == "Said, your application was sent to Acme Bank"
    assert "Backend Developer" in email.text
    assert email.message_id == "<linkedin-001@linkedin.com>"
    assert email.sent_at.year == 2026


def test_decodes_encoded_headers_and_prefers_plain_text():
    email = load("interview_az.eml")
    assert email.sender_name == "Acme Bank HR"
    assert email.subject == "Müsahibə dəvəti"
    assert "müsahibəyə dəvət edirik" in email.text
    assert "<p>" not in email.text


def test_turns_html_only_emails_into_text():
    email = load("greenhouse_received.eml")
    assert "Senior Python Engineer position at Northwind" in email.text
    assert "color" not in email.text
    assert "<b>" not in email.text


def test_html_to_text_keeps_line_breaks():
    assert html_to_text("<p>One &amp; two</p><p>Three<br>Four</p>") == "One & two\nThree\nFour"


def test_survives_a_broken_email():
    email = read_email(b"not really an email")
    assert email.subject == ""
    assert email.sender_address == ""
