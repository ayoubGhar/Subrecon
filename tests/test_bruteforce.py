from __future__ import annotations

import asyncio

from subrecon.bruteforce import run_bruteforce
from subrecon.dns import Resolution, WildcardInfo


class FakeResolver:
    def __init__(self, answers: dict[str, set[str]]) -> None:
        self.answers = answers

    async def resolve_host(self, host: str) -> Resolution:
        return Resolution(host=host, addresses=set(self.answers.get(host, set())))


def test_emits_only_resolving_hosts() -> None:
    pool = FakeResolver(
        {
            "www.example.com": {"203.0.113.10"},
            "api.example.com": {"203.0.113.11"},
        }
    )
    results = asyncio.run(
        run_bruteforce("example.com", ["www", "api", "missing"], pool, concurrency=2)
    )

    assert {item.host for item in results} == {"www.example.com", "api.example.com"}
    assert all(item.resolved for item in results)
    assert all(item.method.value == "bruteforce" for item in results)


def test_annotates_wildcard_matches() -> None:
    wildcard = WildcardInfo(enabled=True, addresses={"203.0.113.5"})
    pool = FakeResolver(
        {
            "random.example.com": {"203.0.113.5"},
            "real.example.com": {"203.0.113.99"},
        }
    )
    results = asyncio.run(run_bruteforce("example.com", ["random", "real"], pool, wildcard))
    by_host = {item.host: item for item in results}

    assert by_host["random.example.com"].wildcard is True
    assert by_host["real.example.com"].wildcard is False


def test_empty_wordlist_yields_nothing() -> None:
    assert asyncio.run(run_bruteforce("example.com", [], FakeResolver({}))) == []
