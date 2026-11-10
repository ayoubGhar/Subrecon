# Architecture

Subrecon is a single-process command-line tool. One run collects names from
three public sources, optionally adds DNS brute-force results, cleans them, and
writes a de-duplicated list. This document explains the moving parts and the
contracts between them.

## 1. Boundaries

In scope:

- three passive providers: crt.sh, AlienVault OTX, HackerTarget;
- optional DNS brute-force with a small bundled wordlist;
- hostname normalization and an engagement scope guard;
- wildcard DNS detection;
- JSONL and TXT output;
- a command-line interface.

Out of scope, on purpose:

- zone transfers (AXFR), virtual-host probing, port scanning;
- providers that need API keys;
- plugin discovery or entry points;
- configuration files, rate limiting, metrics, or an event bus;
- databases or web interfaces.

These exclusions keep the project readable. They are not statements that the
excluded techniques are unimportant.

## 2. Pipeline

```
                 +-------------------+
   domain  --->  | normalize + scope |  scope.py
                 +---------+---------+
                           |
             +-------------+-------------+
             |                           |
      passive stage                active stage
      (always)                     (only with --bruteforce)
             |                           |
   +---------+---------+        +--------+---------+
   | crt.sh  |  OTX    |        | wordlist + DNS   |
   |         | Hacker- |        | lookups          |
   |         | Target  |        |                  |
   +----+----+----+----+        +--------+---------+
        |         |                      |
        +----+----+----------+-----------+
             |               |
       merge by host key     |  models.Subdomain
             |               |
       verify unresolved ----+  dns.Resolver
             |
       wildcard filter
             |
       result object
             |
   +---------+---------+
   | TXT / JSONL files |
   | summary on stderr |
   +-------------------+
```

The engine owns this order. Sources and resolvers do not know about scope,
de-duplication, or output.

## 3. Passive sources

Each provider is one async function with the same shape:

```python
async def source(domain: str, http) -> list[Subdomain]: ...
```

Responsibilities of a source function:

- build the provider URL and parameters;
- call `http.get_json` or `http.get_text`;
- parse the provider-specific payload;
- normalize candidates through `scope.clean_host` and `scope.is_hostname`;
- return `Subdomain` records with method `PASSIVE`, the provider name, and one
  `Evidence` entry;
- log a warning and return `[]` on any failure.

A source never raises for a network or parsing problem and never enforces
scope. This makes failures independent and the engine's job simple.

Provider notes:

- **crt.sh** returns a JSON array of certificate rows. `name_value` can hold
  several newline-separated names and wildcard entries. Skip wildcards.
- **OTX** returns a JSON object with a `passive_dns` list. Each record has a
  `hostname`.
- **HackerTarget** returns CSV text (`host,ip` per line) or a plain-text error
  page. Treat error pages as an empty result.

## 4. DNS resolution and brute-force

`dns.Resolver` wraps one dnspython async resolver configured with public
nameservers. It resolves A, AAAA, and CNAME records concurrently and returns a
`Resolution` (`addresses`, `cnames`, `resolved`).

`bruteforce.run_bruteforce` turns words into `word.domain` candidates and
resolves them in bounded chunks. Only resolved names become `Subdomain`
records. Each record carries:

- method `BRUTEFORCE`;
- source `dns-bruteforce`;
- the address and CNAME sets;
- a wildcard flag calculated from the baseline;
- evidence containing the observed addresses.

One failed lookup is skipped, never fatal. The concurrency limit prevents a
large wordlist from creating thousands of simultaneous queries.

## 5. Data model

`models.Subdomain` is the unit of truth. The important fields:

| Field | Meaning |
| --- | --- |
| `host` | Normalized hostname |
| `method` | `passive` or `bruteforce` |
| `source` | First source that reported it |
| `first_seen`, `last_seen` | UTC timestamps |
| `resolved` | DNS answers were observed |
| `addresses`, `cnames` | Known A/AAAA and CNAME answers |
| `wildcard` | Matches the wildcard baseline |
| `evidence` | Ordered list of `Evidence(source, detail)` |

`key` is the lower-cased hostname without a trailing dot. The engine keeps a
dictionary keyed by it, so every host appears once.

`merge` unions DNS answers, ORs flags, advances `last_seen`, and appends new
evidence. It keeps the first method and source, which explains why the story
of a host is preserved in `evidence` rather than overwritten.

`RunStats` counts what happened and records isolated errors. `EnumerationResult`
bundles the host list, stats, errors, and timestamps for output.

## 6. HTTP client

`http.HttpClient` is a thin wrapper around one `httpx.AsyncClient`:

- lazy import and lazy client creation;
- timeout and redirect handling in one place;
- a descriptive User-Agent;
- retries for transport errors and for 429/500/502/503/504;
- `get_text` and `get_json` only.

Sources accept any object with those two methods. Tests therefore pass a fake
client and never touch the network. The CLI closes the client in a `finally`
block.

## 7. Wildcard detection

A wildcard DNS record answers for names that do not exist. Without a check,
`anything.example.com` resolves and every brute-force word looks successful.

Detection queries a few random labels (`subrecon-<hex>.example.com`). If they
resolve, the returned addresses and CNAMEs form the baseline. A candidate is
flagged when its answers intersect that baseline. The engine drops flagged
records unless `--keep-wildcards` is set.

This is a heuristic. It catches the common `*.domain` case, not every possible
split-horizon or per-name wildcard setup.

## 8. Scope

Scope is enforced in one place, before a candidate enters the result set.

- `clean_host` accepts URLs, ports, userinfo, wildcards, brackets, and IDNA,
  and returns a bare lower-case hostname.
- `is_hostname` rejects empty, malformed, or non-DNS labels.
- `in_scope(host, domain, include, exclude)` accepts the apex and any
  subdomain of the target. Explicit `include` patterns can add hosts outside
  the suffix. `exclude` patterns always win.

Glob patterns use `fnmatch`; plain patterns match the host and its subdomains.
This gives a predictable way to exclude a development branch while keeping the
rest of the tree.

## 9. Errors and limits

- Provider errors: logged, recorded in stats, run continues.
- DNS lookup errors: skipped for that candidate.
- HTTP retries: bounded by `HttpClient.retries`.
- Brute-force concurrency: bounded by `--concurrency`.
- Timeouts: one HTTP timeout and one DNS timeout setting.
- Keyboard interrupt: propagates to the CLI, which returns 130.

There is no unbounded queue, no background daemon, and no global state. A run
owns its client, resolver, stats, and result.

## 10. Output and CLI

`output.py` turns one `EnumerationResult` into files:

- `write_jsonl` — one compact object per host, suitable for piping;
- `write_txt` — one hostname per line;
- `write_outputs` — chooses both from a base path;
- `render_summary` — short human-readable counts.

`cli.py` parses arguments, builds the client and resolver, selects sources,
loads words only when brute-force is enabled, runs the engine, writes optional
files, and prints the summary to **stderr** so stdout stays clean for hosts.

Exit codes are stable: 0 success, 1 unexpected failure, 2 bad input or missing
dependency, 130 interrupted.

## 11. Design decisions

- **Functions over frameworks.** The project has no plugin registry and no
  abstract base classes. Three functions and a dictionary are enough.
- **Passive by default.** Active DNS traffic requires an explicit flag.
- **One model, one writer contract.** Every output format reads the same
  result object, so formats cannot drift apart.
- **Fakes at the boundary.** Tests replace HTTP and DNS, not internal
  functions. This keeps tests fast and deterministic.
- **No credentials.** Public, account-free providers only. There is nothing
  secret to leak or configure.
