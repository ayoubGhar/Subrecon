"""
MODULE: bruteforce.py — WEEK 4

PURPOSE
    Wordlist loading and DNS brute-force with a bounded number of concurrent
    lookups. Wildcard answers are annotated so they can be filtered later.

SPEC
    ARCHITECTURE.md section 3 (brute-force). Acceptance:
    tests/test_bruteforce.py.

WHAT TO IMPLEMENT
    Constant DEFAULT_WORDLIST_RESOURCE = "data/wordlists/subdomains-top100.txt".

    load_words(paths=(), *, include_default=True) -> list of str
      Read the bundled wordlist through importlib.resources when requested,
      then every path as UTF-8 with "~" expanded.
      For each line: strip everything after "#"; skip blanks; skip entries with
      "/", ":", spaces or tabs; normalize with clean_host; skip empty results
      and labels starting with "-".
      De-duplicate while preserving first-seen order.

    async run_bruteforce(domain, words, resolver, wildcard=None, concurrency=100)
        -> list of Subdomain
      Clean the word list and return empty when nothing remains.
      Process words in chunks of concurrency multiplied by 2. For each chunk
      gather the checks with return_exceptions=True; log and skip failed
      workers. Collect only resolved hosts, in input order.
      Use a WildcardInfo() by default.

      For each word:
        - "@" or empty means the apex, otherwise "<word>.<domain>";
        - normalize and validate;
        - resolve with resolver.resolve_host;
        - skip unresolved results and resolver errors;
        - build a Subdomain with method BRUTEFORCE, source "dns-bruteforce",
          resolved True, the address/CNAME sets, the wildcard flag from
          wildcard.matches(...), and evidence whose detail is the sorted
          addresses joined by ", " (fall back to CNAMEs, then "resolved").

CONSTRAINTS
    Never create one task per word. Never raise for one failed lookup.
"""