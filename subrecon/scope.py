"""
MODULE: scope.py — WEEK 1

PURPOSE
    Normalize untrusted host-like input and decide whether a host belongs to the
    engagement. Every candidate passes through this module.

SPEC
    ARCHITECTURE.md section 8 (scope). Acceptance: tests/test_scope.py.

WHAT TO IMPLEMENT
    clean_host(value) -> str
      Normalize a URL, hostname, or wildcard entry to a bare hostname:
        - empty input returns empty;
        - strip whitespace and surrounding quotes, then lower-case;
        - if it contains "://", keep only the URL hostname, otherwise drop
          everything after the first "/";
        - remove userinfo before "@";
        - unwrap a bracketed IPv6 address;
        - drop a numeric port after a single ":";
        - remove leading "*." repeatedly, then strip leading/trailing dots;
        - IDNA-encode to ASCII, ignoring encoding errors.

    is_hostname(value) -> bool
      True when clean_host gives a plausible DNS name:
        - non-empty, at most 253 characters, no spaces;
        - labels are 1 to 63 characters;
        - no label starts or ends with "-";
        - characters limited to a-z, 0-9, "-" and "_".

    in_scope(host, domain, include=(), exclude=()) -> bool
      Normalize host and domain. Return False for an empty host.
      In scope when the host is the domain or ends with "." + domain.
      Otherwise in scope when any include pattern matches.
      Finally out of scope when any exclude pattern matches.
      Pattern rules:
        - patterns with "*", "?" or "[" use fnmatch;
        - a pattern beginning with "*." also matches the bare parent and its
          subdomains;
        - a pattern without glob characters matches itself and its subdomains.

CONSTRAINTS
    No network access and no third-party packages.
"""