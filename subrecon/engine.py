"""
MODULE: engine.py — WEEK 5

PURPOSE
    Run one enumeration: call the selected passive sources, enforce scope,
    de-duplicate, optionally brute-force, verify unresolved hosts, apply the
    wildcard filter, and return a result object.

SPEC
    ARCHITECTURE.md section 2 (pipeline) and section 9 (errors). Acceptance:
    tests/test_engine.py.

WHAT TO IMPLEMENT
    async enumerate_domain(
        domain,
        *,
        http,
        resolver,
        sources=None,
        words=(),
        include=(),
        exclude=(),
        concurrency=100,
        keep_wildcards=False,
    ) -> EnumerationResult

    Steps and rules:

    1. Create RunStats, record the start time, normalize the domain.
       Use sources or the SOURCES mapping from subrecon.sources.
       Keep records in a dict keyed by Subdomain.key.

    2. Passive stage
       Run every selected source concurrently with asyncio.gather and
       return_exceptions=True. A source failure must not stop the others:
       record it with stats.add_error("passive", source_name, exc) and continue.
       For every returned Subdomain:
         - reject out-of-scope hosts with in_scope(...) and increment
           out_of_scope;
         - add new hosts to the dict and increment passive_found;
         - merge duplicates and count a change as a passive find.

    3. Wildcard and brute-force (only when words is non-empty)
       Detect the wildcard baseline with detect_wildcard(resolver, domain).
       Run run_bruteforce(domain, words, resolver, wildcard, concurrency).
       Apply the same scope and de-duplication rules, incrementing active_found.
       Record brute-force failures with stats.add_error("active", "dns-bruteforce", exc).
       When keep_wildcards is false, remove records flagged wildcard and count
       them in wildcard_filtered.

    4. Verification
       For every stored record that is not resolved, call
       resolver.resolve_host. On success mark it resolved and union the
       addresses and CNAMEs. A failure is ignored for that host.
       Re-apply the wildcard baseline to every record.
       Count resolved records into stats.resolved.

    5. Finish
       Mark stats finished and return EnumerationResult with the records sorted
       by key, stats.to_dict(), the error list, and the timestamps.

CONSTRAINTS
    The engine is the only place that enforces scope and de-duplicates.
    One failing source must never abort the run. Never raise for a resolver
    failure during verification.
"""