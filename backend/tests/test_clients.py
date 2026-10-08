import io
import json
from urllib.error import URLError

import pytest

from integrations import clients


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_get_json_sends_the_preview_token(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["token"] = request.get_header("X-preview-token")
        seen["agent"] = request.get_header("User-agent")
        return FakeResponse(json.dumps({"status": "ok"}).encode())

    monkeypatch.setenv("PREVIEW_SECRET", "shared-secret")
    monkeypatch.setattr(clients, "urlopen", fake_urlopen)

    data = clients.get_json("https://radar.example/", "/vacancies", {"q": "python dev", "page": 2})

    assert data == {"status": "ok"}
    assert seen["url"] == "https://radar.example/vacancies?q=python+dev&page=2"
    assert seen["token"] == "shared-secret"
    assert seen["agent"].startswith("jobtrack/")


def test_get_json_without_a_token(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["token"] = request.get_header("X-preview-token")
        return FakeResponse(b"{}")

    monkeypatch.delenv("PREVIEW_SECRET", raising=False)
    monkeypatch.setattr(clients, "urlopen", fake_urlopen)

    clients.get_json("https://rates.example", "/rates")
    assert seen["token"] is None


@pytest.mark.parametrize("error", [URLError("refused"), TimeoutError(), ValueError("not json")])
def test_get_json_turns_failures_into_service_unavailable(monkeypatch, error):
    def fake_urlopen(request, timeout):
        raise error

    monkeypatch.setattr(clients, "urlopen", fake_urlopen)

    with pytest.raises(clients.ServiceUnavailable):
        clients.get_json("https://rates.example", "/rates")
