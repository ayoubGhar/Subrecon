# Six-week plan

This is a lighter version of the original project. You build nine working
modules in six weeks, with one clear theme per week and one checkpoint you can
demonstrate.

- **Time:** about 6–8 hours per week.
- **Tests:** 22 acceptance tests. You never edit them.
- **Starting point:** every module is a written specification, so the test run
  initially fails with 7 collection errors (one per test file).
- **End point:** `subrecon example.com` works, all 22 tests pass, and you can
  explain the pipeline.

Read `ARCHITECTURE.md` once before Week 1. You do not need to memorize it;
use it as a map.

## Setup (before Week 1)

```bash
cd SubreconProject
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Expected at the start:

```
7 errors during collection
```

Each error says a module cannot be imported because its functions do not exist
yet. That is the intended starting state.

## Week-by-week overview

| Week | Theme | Modules | New tests | Cumulative |
| --- | --- | --- | --- | --- |
| 1 | Data and scope | `models.py`, `scope.py` | 9 | 9 |
| 2 | Network primitives | `http.py`, `dns.py` | 2 | 11 |
| 3 | Passive sources | `sources.py` | 3 | 14 |
| 4 | DNS brute-force | `bruteforce.py` | 3 | 17 |
| 5 | Pipeline | `engine.py` | 2 | 19 |
| 6 | Output and CLI | `output.py`, `cli.py` | 3 | 22 |

Week 2 is intentionally light. Use the spare time for the manual HTTP and DNS
checks described below.

---

## Week 1 — Data and scope

**Modules:** `subrecon/models.py`, `subrecon/scope.py`  
**Tests:** `tests/test_models.py` (4), `tests/test_scope.py` (5)  
**Reading:** `ARCHITECTURE.md` sections 5 and 8.

### Tasks

1. Implement `utcnow`, `DiscoveryMethod`, `Evidence`, `Subdomain`, `RunStats`,
   and `EnumerationResult` exactly as `models.py` describes.
2. Implement `clean_host`, `is_hostname`, and `in_scope` in `scope.py`.
3. Run only the two test files while you work:

   ```bash
   python -m pytest tests/test_models.py tests/test_scope.py -q
   ```

### Checkpoint

Nine tests pass, and you can answer:

- Why is `key` a property instead of a stored field?
- What does `merge` preserve, and what does it combine?
- Why does `example.com.evil.test` fail the scope check?

### Pitfalls

- Forgetting to lower-case or strip the trailing dot.
- Treating `*.example.com` as a literal hostname.
- Using a plain suffix check (`endswith`) without the dot, which accepts
  `notexample.com`.
- Making `clean_host` raise instead of returning an empty string.

---

## Week 2 — Network primitives

**Modules:** `subrecon/http.py`, `subrecon/dns.py`  
**Tests:** `tests/test_dns.py` (2)  
**Reading:** `ARCHITECTURE.md` sections 6 and 7.

HTTP has no automated test, because the next week's source tests exercise it
through a fake client. You still need it working.

### Tasks

1. Implement `HttpClient` with lazy import, lazy client creation, two getters,
   bounded retries, and `aclose`.
2. Implement `Resolution`, `Resolver`, `WildcardInfo`, and
   `detect_wildcard`.
3. Run the DNS tests:

   ```bash
   python -m pytest tests/test_dns.py -q
   ```

### Manual checks

HTTP, against a harmless endpoint:

```bash
python - <<'PY'
import asyncio
from subrecon.http import HttpClient

async def main():
    http = HttpClient(timeout=10)
    try:
        text = await http.get_text("https://example.com")
        print("bytes:", len(text))
    finally:
        await http.aclose()

asyncio.run(main())
PY
```

DNS and wildcard detection:

```bash
python - <<'PY'
import asyncio
from subrecon.dns import Resolver, detect_wildcard

async def main():
    resolver = Resolver()
    print(await resolver.resolve_host("example.com"))
    print(await detect_wildcard(resolver, "example.com", samples=2))

asyncio.run(main())
PY
```

### Checkpoint

The two DNS tests pass, the manual HTTP request returns text, and you can
explain why wildcard detection uses random labels.

### Pitfalls

- Creating the `httpx` client at import time.
- Retrying a 404 (only 429/500/502/503/504 are retryable).
- Returning a bare string instead of a `Resolution`.
- Treating NXDOMAIN as an exception that aborts a lookup.

---

## Week 3 — Passive sources

**Module:** `subrecon/sources.py`  
**Tests:** `tests/test_sources.py` (3)  
**Reading:** `ARCHITECTURE.md` section 3.

### Tasks

1. Implement the shared `_make` helper.
2. Implement `crtsh`, `otx`, and `hackertarget`.
3. Register them in `SOURCES`.
4. Run:

   ```bash
   python -m pytest tests/test_sources.py -q
   ```

### Checkpoint

Three tests pass, and you can show the same host arriving from two providers
and appearing once in the engine later.

### Pitfalls

- Forgetting that crt.sh `name_value` can contain several lines.
- Accepting wildcard entries such as `*.example.com`.
- Letting a provider exception escape.
- Following a URL found in provider data (never do this).
- Logging a full response that might contain unrelated names.

---

## Week 4 — DNS brute-force

**Module:** `subrecon/bruteforce.py`  
**Tests:** `tests/test_bruteforce.py` (3)  
**Reading:** `ARCHITECTURE.md` sections 3 and 4.

### Tasks

1. Implement `load_words` and `run_bruteforce`.
2. Keep the bundled wordlist small; do not add a large third-party list.
3. Run:

   ```bash
   python -m pytest tests/test_bruteforce.py -q
   ```

### Checkpoint

Three tests pass, and one failed lookup does not stop the others.

### Pitfalls

- Creating one task per word instead of bounded chunks.
- Reporting unresolved names.
- Forgetting the `@`/apex case.
- Forgetting the wildcard flag.
- Raising when the resolver fails for one candidate.

---

## Week 5 — Pipeline

**Module:** `subrecon/engine.py`  
**Tests:** `tests/test_engine.py` (2)  
**Reading:** `ARCHITECTURE.md` sections 2 and 9.

### Tasks

1. Implement `enumerate_domain` in the order given in the module
   specification.
2. Keep provider calls concurrent and isolated.
3. Run:

   ```bash
   python -m pytest tests/test_engine.py -q
   ```

### Checkpoint

Two tests pass. You can point to the exact lines that enforce scope, merge
duplicates, and isolate a failing source.

### Pitfalls

- Letting `asyncio.gather` propagate one provider's exception.
- Counting out-of-scope hosts in `passive_found`.
- Forgetting to merge evidence from duplicate sources.
- Verifying a host that already resolved.
- Dropping wildcard records before counting them.

---

## Week 6 — Output and CLI

**Modules:** `subrecon/output.py`, `subrecon/cli.py`  
**Tests:** `tests/test_output.py` (3)  
**Reading:** `ARCHITECTURE.md` sections 10 and 11.

### Tasks

1. Implement the three writers and `render_summary`.
2. Implement `build_parser` and `main` with the flags, defaults, and exit codes
   in the specification.
3. Run the full suite:

   ```bash
   python -m pytest -q
   ```

4. Run the demo below.

### Demo (the final checkpoint)

Use a domain you own or a reserved example. Passive only first:

```bash
subrecon example.com --print-hosts
```

Then with output files and brute-force disabled:

```bash
subrecon example.com -o out/example --format jsonl,txt
head -n 3 out/example.txt
head -n 1 out/example.jsonl
```

Finally, show that the scope guard works:

```bash
subrecon example.com --exclude www.example.com --print-hosts
```

The demo must show:

- a summary on stderr;
- hostnames on stdout only with `--print-hosts`;
- two output files with the same host set;
- an excluded host absent from both.

### Pitfalls

- Printing the summary to stdout.
- Writing files when `-o` is absent.
- Crashing instead of returning exit code 2 for a bad domain.
- Forgetting to close the HTTP client.
- Letting `--bruteforce` default to on.

---

## Assessment

| Area | Weight | What is checked |
| --- | --- | --- |
| Acceptance tests | 50% | All 22 pass, no test edits |
| Module contracts | 20% | Signatures and behavior match the specifications |
| Error handling | 10% | Provider and resolver failures are isolated |
| Code clarity | 10% | Small functions, clear names, no dead code |
| Demo and explanation | 10% | Tool runs; student explains the pipeline |

## Definition of done

- [ ] `python -m pytest -q` reports 22 passed.
- [ ] No file in `tests/` was edited.
- [ ] `subrecon example.com` runs with passive sources only.
- [ ] `--bruteforce` is opt-in and documented.
- [ ] TXT and JSONL contain the same hosts.
- [ ] No secrets, API keys, or third-party provider accounts were added.
- [ ] The student can draw the pipeline from memory.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `ModuleNotFoundError: subrecon` | Run `pip install -e .` inside the venv |
| Tests still fail at collection | A module still has no implementation |
| Every brute-force name resolves | Wildcard detection is missing or wrong |
| A provider always returns `[]` | Its payload shape changed; check the logged warning |
| Summary appears in a pipeline | It is being printed to stdout instead of stderr |
| `RuntimeError: Event loop is closed` | A client or resolver was reused across `asyncio.run` calls |

## Instructor notes

- Keep the scope fixed. Adding providers, AXFR, vhost probing, or a plugin
  system recreates the complexity this version removes.
- Review Week 1 carefully. Scope and de-duplication bugs surface in every
  later week.
- Week 2 has slack by design; use it for the manual checks, not new features.
- The automated suite does not cover the CLI. Grade the demo and the exit
  codes manually.
- Network access may be unavailable in class. The tests use fakes and should
  pass offline; run the live demo from a prepared environment.
