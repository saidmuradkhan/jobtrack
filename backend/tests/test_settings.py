import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent


def load_settings(names, **env):
    """Read settings in a fresh process, because they are built once on import."""
    code = (
        "import json, django\n"
        "from django.conf import settings\n"
        "django.setup()\n"
        f"print(json.dumps({{n: getattr(settings, n) for n in {names!r}}}, default=str))\n"
    )
    prefixes = ("DATABASE_", "DJANGO_", "VERCEL")
    clean = {k: v for k, v in os.environ.items() if not k.startswith(prefixes)}
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND,
        env={**clean, "DJANGO_SETTINGS_MODULE": "config.settings", **env},
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_sqlite_without_database_url():
    db = load_settings(["DATABASES"])["DATABASES"]["default"]
    assert db["ENGINE"] == "django.db.backends.sqlite3"
    assert db["NAME"].endswith("db.sqlite3")


def test_postgres_from_database_url():
    url = "postgres://jobtrack:pw@ep-test-pooler.neon.tech/jobtrack?sslmode=require"
    db = load_settings(["DATABASES"], DATABASE_URL=url)["DATABASES"]["default"]
    assert db["ENGINE"] == "django.db.backends.postgresql"
    assert db["HOST"] == "ep-test-pooler.neon.tech"
    assert db["NAME"] == "jobtrack"
    assert db["OPTIONS"]["sslmode"] == "require"
    assert db["DISABLE_SERVER_SIDE_CURSORS"] is True


def test_cors_allows_only_the_frontend():
    found = load_settings(["CORS_ALLOWED_ORIGINS"], FRONTEND_URL="https://jobs.example.dev/")
    assert found["CORS_ALLOWED_ORIGINS"] == ["https://jobs.example.dev"]
    assert load_settings(["CORS_ALLOWED_ORIGINS"])["CORS_ALLOWED_ORIGINS"] == []


def test_production_trusts_the_https_header_from_vercel():
    names = ["DEBUG", "SECURE_PROXY_SSL_HEADER", "SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE"]
    found = load_settings(names, DJANGO_DEBUG="0", DJANGO_SECRET_KEY="test-only-key")
    assert found["DEBUG"] is False
    assert found["SECURE_PROXY_SSL_HEADER"] == ["HTTP_X_FORWARDED_PROTO", "https"]
    assert found["SESSION_COOKIE_SECURE"] is True
    assert found["CSRF_COOKIE_SECURE"] is True


def test_debug_is_off_on_vercel_by_default():
    found = load_settings(
        ["DEBUG", "ALLOWED_HOSTS"],
        VERCEL="1",
        VERCEL_URL="jobtrack-abc123.vercel.app",
        DJANGO_SECRET_KEY="test-only-key",
        DJANGO_ALLOWED_HOSTS="jobs-api.example.dev",
    )
    assert found["DEBUG"] is False
    assert found["ALLOWED_HOSTS"] == ["jobs-api.example.dev", "jobtrack-abc123.vercel.app"]


def test_vercel_refuses_to_start_without_a_secret_key():
    with pytest.raises(subprocess.CalledProcessError) as error:
        load_settings(["DEBUG"], VERCEL="1")
    assert "DJANGO_SECRET_KEY must be set" in error.value.stderr
