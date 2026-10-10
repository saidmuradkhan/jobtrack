from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from inbox.processing import process_email
from inbox.reading import read_email


class Command(BaseCommand):
    help = "Handle a saved .eml file as if it was forwarded by the user (for local testing)."

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path)
        parser.add_argument("--user", required=True, help="username")

    def handle(self, *args, **options):
        try:
            user = get_user_model().objects.get(username=options["user"])
        except get_user_model().DoesNotExist as error:
            raise CommandError(f"No user called {options['user']}") from error
        if not options["path"].is_file():
            raise CommandError(f"No file at {options['path']}")

        record = process_email(user, read_email(options["path"].read_bytes()))
        target = record.application or "no application"
        self.stdout.write(f"{record.get_outcome_display()}: {record.subject} -> {target}")
