"""Temporary login that keeps the site private until it is ready for review.

It is on only while PREVIEW_USER and PREVIEW_PASSWORD are set.
"""

import hmac
import os

from django.conf import settings
from django.core import signing

COOKIE_NAME = "preview_session"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60
SALT = "preview-gate"


def credentials():
    user = os.environ.get("PREVIEW_USER", "")
    password = os.environ.get("PREVIEW_PASSWORD", "")
    if not user or not password:
        return None
    return user, password


def secret():
    return os.environ.get("PREVIEW_SECRET") or os.environ.get("PREVIEW_PASSWORD", "")


def check_credentials(user, password):
    expected_user, expected_password = credentials()
    user_ok = hmac.compare_digest(user.encode(), expected_user.encode())
    password_ok = hmac.compare_digest(password.encode(), expected_password.encode())
    return user_ok and password_ok


def make_cookie_value():
    return signing.dumps(credentials()[0], key=secret(), salt=SALT)


def cookie_is_valid(value):
    try:
        signing.loads(value, key=secret(), salt=SALT, max_age=COOKIE_MAX_AGE)
    except signing.BadSignature:
        return False
    return True


def allows(request):
    if credentials() is None:
        return True
    if request.path in {"/health", "/preview/login"} or request.method == "OPTIONS":
        return True
    token = request.headers.get("X-Preview-Token", "")
    if token and hmac.compare_digest(token.encode(), secret().encode()):
        return True
    return cookie_is_valid(request.COOKIES.get(COOKIE_NAME, ""))


def safe_next(value):
    """Only go back to this site or to the frontend after logging in."""
    if value and value.startswith("/") and not value.startswith("//"):
        return value
    frontend = settings.FRONTEND_URL.rstrip("/")
    if frontend and value and (value == frontend or value.startswith(frontend + "/")):
        return value
    return "/health"
