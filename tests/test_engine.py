from __future__ import annotations

import asyncio

from subrecon.dns import Resolution
from subrecon.engine import enumerate_domain
from subrecon.models import DiscoveryMethod, Evidence, Subdomain


class FakeResolver:
    def __init__(self, answers: dict[str, set[str]] | None = None) -> None:
        self.answers = answers or {}

    async def resolve_host(self, host: str) -> Resolution:
        return Resolution(host=host, addresses=set(self.answers.get(host, set())))


async def fake_source(domain: str, http) -> list[Subdomain]:
    return [
        Subdomain(host=f"api.{domain}", method=DiscoveryMethod.PASSIVE, source="fake",
                  evidence=[Evidence(source="fake")]),
        Subdomain(host=f"noise.{domain}", method=DiscoveryMethod.PASSIVE, source="fake",
                  evidence=[Evidence(source="fake")]),
        Subdomain(host="outside.test", method=DiscoveryMethod.PASSIVE, source="fake",
                  evidence=[Evidence(source="fake")]),
    ]


def test_engine_enforces_scope_and_verifies() -> None:
    resolver = FakeResolver({"api.example.com": {"203.0.113.10"}})
    result = asyncio.run(
        enumerate_domain(
            "example.com",
            http=object(),
            resolver=resolver,
            sources={"fake": fake_source},
        )
    )

    hosts = {item.host: item for item in result.subdomains}
    assert set(hosts) == {"api.example.com", "noise.example.com"}
    assert hosts["api.example.com"].resolved is True
    assert hosts["noise.example.com"].resolved is False
    assert result.stats["out_of_scope"] == 1
    assert result.stats["passive_found"] == 2
    assert result.stats["resolved"] == 1


async def broken_source(domain: str, http) -> list[Subdomain]:
    raise RuntimeError("provider broke")


async def good_source(domain: str, http) -> list[Subdomain]:
    return [
        Subdomain(host=f"one.{domain}", method=DiscoveryMethod.PASSIVE, source="good",
                  evidence=[Evidence(source="good")])
    ]


def test_engine_isolates_source_failures() -> None:
    result = asyncio.run(
        enumerate_domain(
            "example.com",
            http=object(),
            resolver=FakeResolver(),
            sources={"good": good_source, "broken": broken_source},
        )
    )

    assert {item.host for item in result.subdomains} == {"one.example.com"}
    assert len(result.errors) == 1
    assert result.errors[0]["source"] == "broken"
    assert result.errors[0]["type"] == "RuntimeError"
