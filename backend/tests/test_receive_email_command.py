from io import StringIO
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command

FIXTURES = Path(__file__).parent / "fixtures" / "emails"


@pytest.mark.django_db
def test_command_handles_a_saved_email(user):
    out = StringIO()
    call_command("receive_email", FIXTURES / "linkedin_applied.eml", user="said", stdout=out)
    assert "Added a new application" in out.getvalue()
    assert "Backend Developer at Acme Bank" in out.getvalue()


@pytest.mark.django_db
def test_command_needs_a_real_user_and_file(user):
    with pytest.raises(CommandError):
        call_command("receive_email", FIXTURES / "offer.eml", user="nobody")
    with pytest.raises(CommandError):
        call_command("receive_email", FIXTURES / "missing.eml", user="said")
