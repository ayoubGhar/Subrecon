from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from subrecon.models import DiscoveryMethod, EnumerationResult, Evidence, Subdomain
from subrecon.output import render_summary, write_jsonl, write_txt


def sample_result() -> EnumerationResult:
    now = datetime.now(UTC)
    item = Subdomain(
        host="api.example.com",
        method=DiscoveryMethod.PASSIVE,
        source="crtsh",
        resolved=True,
        addresses={"203.0.113.10"},
        evidence=[Evidence(source="crtsh", detail="ct")],
    )
    return EnumerationResult(
        domain="example.com",
        subdomains=[item],
        stats={
            "duration_seconds": 1.0,
            "passive_found": 1,
            "active_found": 0,
            "resolved": 1,
            "wildcard_filtered": 0,
            "out_of_scope": 0,
            "errors": [],
        },
        errors=[],
        started_at=now,
        finished_at=now,
    )


def test_write_jsonl(tmp_path: Path) -> None:
    path = write_jsonl(sample_result(), tmp_path / "out" / "scan.jsonl")
    line = json.loads(path.read_text(encoding="utf-8").strip())
    assert line["host"] == "api.example.com"
    assert line["method"] == "passive"


def test_write_txt(tmp_path: Path) -> None:
    path = write_txt(sample_result(), tmp_path / "scan.txt")
    assert path.read_text(encoding="utf-8").strip() == "api.example.com"


def test_render_summary() -> None:
    summary = render_summary(sample_result())
    assert "Subrecon summary" in summary
    assert "example.com" in summary
    assert "discovered   : 1" in summary
