import os
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from applications.models import Application
from inbox.models import InboundEmail, Inbox

S = Application.Status

# company, position, status, days ago, salary, currency, notes
APPLICATIONS = [
    (
        "Caspian Digital",
        "Backend Developer (Python)",
        S.INTERVIEW,
        3,
        2800,
        "AZN",
        "Second round with the team lead on Thursday.",
    ),
    ("Absheron Payments", "Django Developer", S.APPLIED, 5, 3200, "AZN", ""),
    (
        "Khazar Logistics",
        "Full-stack Developer",
        S.OFFER,
        21,
        2500,
        "USD",
        "Offer until the end of the month, asked for remote Fridays.",
    ),
    (
        "Baku Cloud Lab",
        "Junior DevOps Engineer",
        S.REJECTED,
        30,
        None,
        "AZN",
        "They chose someone with more Kubernetes experience.",
    ),
    ("Ganja AgroTech", "Python Developer", S.APPLIED, 8, 2000, "AZN", ""),
    (
        "Shirvan Retail",
        "Data Analyst",
        S.WISHLIST,
        1,
        None,
        "AZN",
        "Looks interesting, update the CV with the SQL project first.",
    ),
    (
        "Northwind Analytics",
        "Backend Engineer",
        S.INTERVIEW,
        12,
        3000,
        "USD",
        "Take-home task: small REST API with tests.",
    ),
    ("Lankaran Health", "Software Engineer", S.APPLIED, 15, 2400, "AZN", ""),
    ("Sumgait Energy", "Internal Tools Developer", S.REJECTED, 40, 1800, "AZN", ""),
    ("Qabala Travel", "React Developer", S.WISHLIST, 2, 2200, "AZN", ""),
    (
        "Contoso Bank",
        "Junior Backend Developer",
        S.APPLIED,
        10,
        None,
        "AZN",
        "Referral from a former classmate.",
    ),
    ("Mingachevir Media", "Web Developer", S.REJECTED, 25, 1500, "AZN", ""),
]

# company, subject, sender, outcome, status, previous status
EMAILS = [
    (
        "Caspian Digital",
        "Interview invitation: Backend Developer (Python)",
        "Caspian Digital HR <hr@caspian-digital.example>",
        InboundEmail.Outcome.UPDATED,
        S.INTERVIEW,
        S.APPLIED,
    ),
    (
        "Absheron Payments",
        "Thank you for applying to Absheron Payments",
        "Absheron Payments <jobs@absheron-payments.example>",
        InboundEmail.Outcome.CREATED,
        S.APPLIED,
        "",
    ),
    (
        "Baku Cloud Lab",
        "Your application for Junior DevOps Engineer",
        "Baku Cloud Lab <careers@bakucloudlab.example>",
        InboundEmail.Outcome.UPDATED,
        S.REJECTED,
        S.APPLIED,
    ),
    (
        "Azure Coast Studio",
        "Offer letter: Frontend Developer",
        "Azure Coast Studio <people@azurecoast.example>",
        InboundEmail.Outcome.PENDING,
        S.OFFER,
        "",
    ),
]


class Command(BaseCommand):
    help = "Create a demo user with sample applications and email updates."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", help="defaults to DEMO_PASSWORD or a random one")
        parser.add_argument(
            "--reset", action="store_true", help="replace the data of an existing user"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        password = options["password"] or os.environ.get("DEMO_PASSWORD", "")
        user = User.objects.filter(username=username).first()

        if user and user.applications.exists() and not options["reset"]:
            raise CommandError(f"{username} already has applications, add --reset to replace them")

        printed_password = ""
        if user is None:
            if not password:
                password = printed_password = secrets.token_urlsafe(12)
            user = User.objects.create_user(username=username, password=password)
        elif password:
            user.set_password(password)
            user.save()

        user.applications.all().delete()
        user.inbound_emails.all().delete()
        Inbox.objects.get_or_create(user=user)

        today = timezone.localdate()
        by_company = {}
        for company, position, status, days_ago, salary, currency, notes in APPLICATIONS:
            by_company[company] = Application.objects.create(
                user=user,
                company=company,
                position=position,
                status=status,
                applied_on=today - timedelta(days=days_ago),
                salary=salary,
                currency=currency,
                notes=notes,
            )

        for company, subject, sender, outcome, status, previous in EMAILS:
            application = by_company.get(company)
            InboundEmail.objects.create(
                user=user,
                application=application,
                sender=sender,
                subject=subject,
                status=status,
                company=company,
                position=application.position if application else "Frontend Developer",
                outcome=outcome,
                previous_status=previous,
            )

        self.stdout.write(
            f"{username}: {len(APPLICATIONS)} applications and {len(EMAILS)} email updates"
        )
        if printed_password:
            self.stdout.write(f"Password: {printed_password}")
