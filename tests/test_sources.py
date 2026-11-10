from __future__ import annotations

import asyncio

from subrecon.models import Subdomain
from subrecon.sources import crtsh, hackertarget, otx


class FakeHttp:
    def __init__(self, *, json_payload=None, text_payload: str = "") -> None:
        self.json_payload = json_payload
        self.text_payload = text_payload

    async def get_json(self, url, *, params=None, headers=None):
        return self.json_payload

    async def get_text(self, url, *, params=None, headers=None):
        return self.text_payload


def run(source, http) -> list[Subdomain]:
    return asyncio.run(source("example.com", http))


def test_crtsh_parses_deduplicates_and_skips_wildcards() -> None:
    payload = [
        {
            "id": 1,
            "name_value": "api.example.com\n*.example.com\nAPI.example.com\nbad host",
        },
        {"id": 2, "name_value": None},
        "junk",
    ]
    hosts = [item.host for item in run(crtsh, FakeHttp(json_payload=payload))]
    assert hosts == ["api.example.com"]


def test_otx_ignores_missing_and_duplicate_hostnames() -> None:
    payload = {
        "passive_dns": [
            {"hostname": "api.example.com"},
            {"hostname": "api.example.com"},
            {"hostname": None},
            {"hostname": "*"},
            {"not_hostname": "x"},
        ]
    }
    hosts = [item.host for item in run(otx, FakeHttp(json_payload=payload))]
    assert hosts == ["api.example.com"]


def test_hackertarget_parses_csv_and_rejects_error_pages() -> None:
    text = "www.example.com,203.0.113.10\napi.example.com,203.0.113.11\n\n"
    hosts = [item.host for item in run(hackertarget, FakeHttp(text_payload=text))]
    assert hosts == ["www.example.com", "api.example.com"]

    error = FakeHttp(text_payload="error check your search parameter")
    assert run(hackertarget, error) == []
