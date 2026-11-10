"""
MODULE: dns.py — WEEK 2

PURPOSE
    Async DNS resolution and wildcard detection. Brute-force and verification
    both use this module.

SPEC
    ARCHITECTURE.md sections 3 and 7 (DNS and wildcard). Acceptance:
    tests/test_dns.py plus the manual DNS check in the plan.

WHAT TO IMPLEMENT
    class Resolution — dataclass (slots).
      Fields: host (str); addresses (set of str); cnames (set of str).
      Property resolved: True when addresses or cnames is non-empty.

    class Resolver
      Constructor: Resolver(servers=None, *, timeout=3.0, attempts=2).
      Default servers are 1.1.1.1, 8.8.8.8 and 9.9.9.9.
      Build one dnspython async resolver lazily with configure=False, all the
      servers as nameservers, the timeout, and lifetime 1.5 times the timeout.
      Raise MissingDependency when dnspython is missing.

      async resolve(host, rdtype="A") -> list of str
        Normalize the host with clean_host. Return empty for an empty host.
        Try up to attempts times. NXDOMAIN and NoAnswer return empty
        immediately. Timeouts and other DNS errors are retried.
        Return the answer strings with trailing dots removed; return empty when
        there is no answer set.

      async resolve_host(host) -> Resolution
        Resolve A, AAAA and CNAME concurrently with gather and
        return_exceptions=True. Merge CNAME answers into cnames and A/AAAA into
        addresses. Ignore failed queries.

    class WildcardInfo — dataclass (slots).
      Fields: enabled (bool, False); addresses (set); cnames (set);
      samples (list of str).
      matches(addresses, cnames) -> bool:
        False when disabled; otherwise True when the supplied addresses or
        CNAMEs intersect the baseline sets.

    async detect_wildcard(resolver, domain, samples=3) -> WildcardInfo
      Query the requested number of random "subrecon-<hex>.domain" labels
      with resolver.resolve_host, concurrently, tolerating failures. Union all
      answers, record the labels, and set enabled when at least one address or
      CNAME was seen.

CONSTRAINTS
    Import dnspython lazily. Never raise for NXDOMAIN or timeouts.
"""