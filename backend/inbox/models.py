import re
import secrets

from django.conf import settings
from django.db import models


def new_key():
    return secrets.token_hex(5)


class Inbox(models.Model):
    """A private address the user forwards job emails to."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inbox"
    )
    key = models.CharField(max_length=20, unique=True, default=new_key)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    @property
    def address(self):
        # Usernames may contain "@" or "+", which do not belong in an address.
        name = re.sub(r"[^a-z0-9]", "", self.user.username.lower())[:20] or "user"
        return f"{name}-{self.key}@{settings.INBOX_DOMAIN}"


class InboundEmail(models.Model):
    """What we understood from one forwarded email. The full text is not kept."""

    class Outcome(models.TextChoices):
        CREATED = "created", "Added a new application"
        UPDATED = "updated", "Changed the status"
        UNCHANGED = "unchanged", "Nothing to change"
        PENDING = "pending", "Waiting for you to confirm"
        DISMISSED = "dismissed", "Dismissed"
        IGNORED = "ignored", "Not about a job"
        FORWARDING = "forwarding", "Gmail forwarding confirmation"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inbound_emails"
    )
    application = models.ForeignKey(
        "applications.Application",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails",
    )
    message_id = models.CharField(max_length=300, blank=True)
    sender = models.CharField(max_length=300)
    subject = models.CharField(max_length=300, blank=True)
    snippet = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    outcome = models.CharField(max_length=20, choices=Outcome.choices)
    previous_status = models.CharField(max_length=20, blank=True)
    forwarding_code = models.CharField(max_length=20, blank=True)
    forwarding_link = models.URLField(max_length=500, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "message_id"],
                condition=~models.Q(message_id=""),
                name="one_inbound_email_per_message",
            )
        ]

    def __str__(self):
        return f"{self.subject} ({self.outcome})"
