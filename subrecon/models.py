"""
MODULE: models.py — WEEK 1

PURPOSE
    The data model for one run: a discovered host, its evidence, run counters,
    and the final result object.

SPEC
    ARCHITECTURE.md section 5 (data model). Acceptance: tests/test_models.py.

WHAT TO IMPLEMENT
    utcnow() -> datetime
      Current time as a timezone-aware UTC datetime.

    class DiscoveryMethod — string enum with exactly:
      PASSIVE = "passive"
      BRUTEFORCE = "bruteforce"

    class Evidence — immutable dataclass (frozen, slots).
      Fields: source (str), detail (str, default empty).
      Method to_dict() returns {"source": ..., "detail": ...}.

    class Subdomain — dataclass (slots).
      Fields, in this order:
        host (str)
        method (DiscoveryMethod)
        source (str)
        first_seen (datetime, default utcnow)
        last_seen (datetime, default utcnow)
        resolved (bool, False)
        addresses (set of str, empty)
        cnames (set of str, empty)
        wildcard (bool, False)
        evidence (list of Evidence, empty)

      Property key: host lower-cased with trailing dots removed. This is the
      de-duplication identity.

      Method merge(other) -> bool:
        - union addresses and cnames;
        - OR the resolved and wildcard flags;
        - advance last_seen to the later timestamp;
        - append evidence entries only when not already present;
        - keep the original method and source labels.
        Return True only when resolved, wildcard, addresses, cnames, or the
        number of evidence entries changed.

      Method to_dict() -> dict with exactly these keys:
        host, method (enum string), source, first_seen and last_seen (ISO 8601),
        resolved, addresses and cnames (sorted lists), wildcard,
        evidence (list of dicts).

    class RunStats — dataclass (slots).
      Fields: passive_found, active_found, resolved, wildcard_filtered,
      out_of_scope (int, default 0); errors (list of dict); started_at
      (datetime, default utcnow); finished_at (datetime or None).
      finish(): set finished_at to now.
      Property duration_seconds: non-negative seconds between the timestamps.
      add_error(stage, source, exc): append {"stage", "source", "type", "error"}.
        For an exception, type is the class name and error its message. For a
        string, type is "Error".
      to_dict(): duration rounded to 3 decimals, all counters, a copy of errors.

    class EnumerationResult — dataclass (slots).
      Fields: domain, subdomains (list), stats (dict), errors (list),
      started_at and finished_at (datetime).
      to_dict(): domain, ISO timestamps, stats, errors, serialized subdomains.

CONSTRAINTS
    Standard library only. Keep every field and method name exactly as written.
"""