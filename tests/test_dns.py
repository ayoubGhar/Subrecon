from __future__ import annotations

import asyncio

from subrecon.dns import Resolution, WildcardInfo, detect_wildcard


def test_wildcard_matches_addresses_and_cnames() -> None:
    info = WildcardInfo(enabled=True, addresses={"203.0.113.5"}, cnames={"lb.example.net"})
    assert info.matches({"203.0.113.5"}, set()) is True
    assert info.matches(set(), {"lb.example.net"}) is True
    assert info.matches({"203.0.113.99"}, set()) is False

    disabled = WildcardInfo(addresses={"203.0.113.5"})
    assert disabled.matches({"203.0.113.5"}, set()) is False


class FakeResolver:
    def __init__(self, addresses: set[str]) -> None:
        self.addresses = addresses

    async def resolve_host(self, host: str) -> Resolution:
        return Resolution(host=host, addresses=set(self.addresses))


def test_detects_wildcard_from_random_labels() -> None:
    info = asyncio.run(detect_wildcard(FakeResolver({"203.0.113.5"}), "example.com", samples=3))
    assert info.enabled is True
    assert info.addresses == {"203.0.113.5"}
    assert len(info.samples) == 3
    assert all(label.endswith(".example.com") for label in info.samples)

    empty = asyncio.run(detect_wildcard(FakeResolver(set()), "example.com", samples=3))
    assert empty.enabled is False
