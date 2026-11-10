from __future__ import annotations

from subrecon.models import DiscoveryMethod, Evidence, RunStats, Subdomain, utcnow


def make(host: str = "api.example.com") -> Subdomain:
    return Subdomain(
        host=host,
        method=DiscoveryMethod.PASSIVE,
        source="crtsh",
        evidence=[Evidence(source="crtsh", detail="ct")],
    )


def test_key_normalization() -> None:
    assert make("API.Example.COM.").key == "api.example.com"


def test_merge_unions_and_preserves_provenance() -> None:
    first = make()
    second = Subdomain(
        host="api.example.com",
        method=DiscoveryMethod.BRUTEFORCE,
        source="dns-bruteforce",
        resolved=True,
        addresses={"203.0.113.10"},
        evidence=[Evidence(source="dns-bruteforce", detail="A record")],
    )

    assert first.merge(second) is True
    assert first.source == "crtsh"
    assert first.resolved is True
    assert first.addresses == {"203.0.113.10"}
    assert len(first.evidence) == 2
    assert first.merge(second) is False


def test_to_dict_contract() -> None:
    item = make()
    item.resolved = True
    item.addresses = {"203.0.113.11", "203.0.113.10"}

    payload = item.to_dict()
    assert payload["host"] == "api.example.com"
    assert payload["method"] == "passive"
    assert payload["addresses"] == ["203.0.113.10", "203.0.113.11"]
    assert payload["evidence"][0]["source"] == "crtsh"


def test_run_stats_errors_and_duration() -> None:
    stats = RunStats()
    stats.add_error("passive", "crtsh", TimeoutError("slow"))
    stats.add_error("active", "bruteforce", "bad response")
    stats.finish()

    payload = stats.to_dict()
    assert payload["errors"][0]["type"] == "TimeoutError"
    assert payload["errors"][1]["type"] == "Error"
    assert payload["duration_seconds"] >= 0
    assert stats.started_at <= (stats.finished_at or utcnow())
