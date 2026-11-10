from __future__ import annotations

from subrecon.scope import clean_host, in_scope, is_hostname


def test_clean_host_handles_urls_ports_and_wildcards() -> None:
    assert clean_host("https://user:pass@WWW.Example.COM:8443/path") == "www.example.com"
    assert clean_host("*.dev.example.com.") == "dev.example.com"
    assert clean_host("example.com:443") == "example.com"
    assert clean_host("example.com.") == "example.com"
    assert clean_host("") == ""


def test_clean_host_idna() -> None:
    assert clean_host("bücher.example") == "xn--bcher-kva.example"


def test_is_hostname() -> None:
    assert is_hostname("api.example.com")
    assert is_hostname("_dmarc.example.com")
    assert not is_hostname("not a host")
    assert not is_hostname("")
    assert not is_hostname("-bad.example.com")


def test_in_scope_apex_and_subdomains() -> None:
    assert in_scope("example.com", "example.com")
    assert in_scope("api.example.com", "example.com")
    assert in_scope("deep.api.example.com", "example.com")
    assert not in_scope("example.com.evil.test", "example.com")
    assert not in_scope("notexample.com", "example.com")


def test_in_scope_include_and_exclude() -> None:
    assert in_scope("partner.example.net", "example.com", include=["partner.example.net"])
    assert in_scope("www.partner.example.net", "example.com", include=["partner.example.net"])
    assert not in_scope(
        "dev.example.com",
        "example.com",
        exclude=["dev.example.com"],
    )
    assert not in_scope(
        "api.dev.example.com",
        "example.com",
        exclude=["dev.example.com"],
    )
    assert not in_scope(
        "db.internal.example.com",
        "example.com",
        exclude=["*.internal.example.com"],
    )
