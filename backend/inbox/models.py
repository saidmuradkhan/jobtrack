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
