"""Small JSON client for the other two services: az-job-radar and cbar-rates."""

import json
import os
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = "jobtrack/0.1 (+https://github.com/saidmuradkhan/jobtrack)"


class ServiceUnavailable(Exception):
    pass


def get_json(base_url, path, params=None):
    url = base_url.rstrip("/") + path
    if params:
        url += "?" + urlencode(params, doseq=True)

    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    # Lets this server through the preview login of the other two sites.
    token = os.environ.get("PREVIEW_SECRET")
    if token:
        headers["X-Preview-Token"] = token

    try:
        with urlopen(Request(url, headers=headers), timeout=10) as response:
            return json.load(response)
    except (URLError, TimeoutError, ValueError) as error:
        raise ServiceUnavailable(f"{url}: {error}") from error
