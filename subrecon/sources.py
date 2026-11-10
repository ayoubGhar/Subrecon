"""
MODULE: sources.py — WEEK 3

PURPOSE
    Three passive providers in one small module. Each function asks a public
    service for names and returns Subdomain records; the engine owns scope,
    de-duplication and verification.

SPEC
    ARCHITECTURE.md section 4 (passive sources). Acceptance: tests/test_sources.py.

WHAT TO IMPLEMENT
    A private helper _make(host, source, detail) -> Subdomain or None
      Normalize with clean_host, return None for an invalid hostname, otherwise
      build a Subdomain with method PASSIVE, the given source, and one Evidence
      entry. Every provider uses this helper.

    async crtsh(domain, http) -> list of Subdomain
      GET https://crt.sh/ with params q = "%.<domain>" and output = "json"
      using http.get_json.
      On any request error, log a warning and return an empty list.
      The payload must be a list. For each dict entry read name_value; skip
      non-strings. Split on newlines, skip candidates starting with "*.",
      normalize and validate, and drop duplicates.
      Detail: "certificate transparency".

    async otx(domain, http) -> list of Subdomain
      GET
      https://otx.alienvault.com/api/v1/indicators/domain/<domain>/passive_dns
      with http.get_json. On error, log and return empty.
      The payload must be a dict; read its passive_dns list.
      For each dict record read hostname; ignore non-strings, invalid names,
      "*", and duplicates. Detail: "OTX passive DNS".

    async hackertarget(domain, http) -> list of Subdomain
      GET https://api.hackertarget.com/hostsearch/ with params q = domain
      using http.get_text. On error, log and return empty.
      Treat the response as an error and return empty when it contains
      "api count exceeded" (case-insensitive), or when the first non-empty line
      has no comma and starts with "error".
      Otherwise split each "host,ip" line, normalize and validate the host,
      drop duplicates. Detail: "hostsearch".

    SOURCES = {"crtsh": crtsh, "otx": otx, "hackertarget": hackertarget}

CONSTRAINTS
    Never raise for a provider failure: log and return an empty list.
    Never fetch a URL supplied by provider data. Never log credentials.
"""