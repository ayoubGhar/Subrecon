"""
MODULE: http.py — WEEK 2

PURPOSE
    One small shared HTTP client for the passive sources, with retries and a
    timeout. Vhost probing and rate limiting are out of scope.

SPEC
    ARCHITECTURE.md section 6 (HTTP). Acceptance: verified by the Week 3 source
    tests with a fake client, plus the manual smoke test in the plan.

WHAT TO IMPLEMENT
    Retryable status codes: 429, 500, 502, 503, 504.

    class HttpClient
      Constructor: HttpClient(*, timeout=20.0, retries=2). Store the settings.
      Keep the httpx client lazy and create it on first use.

      Import httpx lazily. When it is missing, raise MissingDependency with an
      install hint.

      Build the client with the timeout, follow_redirects enabled, and a
      User-Agent header "Subrecon/0.1 (+authorized-recon)".

      async get_text(url, *, params=None, headers=None) -> str
        GET the URL. Retry transport errors and retryable statuses up to the
        configured number of retries, sleeping 0.5 seconds before each retry.
        Raise for a non-success status and return the response text.

      async get_json(url, *, params=None, headers=None) -> parsed JSON
        Same retry behavior, returning parsed JSON.

      async aclose()
        Close the underlying client when it exists. Safe to call twice.

CONSTRAINTS
    Sources may receive a fake object with only get_text and get_json, so the
    source code must not depend on any other attribute.
"""