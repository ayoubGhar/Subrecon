# Subrecon — student project

A small, readable subdomain enumerator written in Python. You will build it one
module at a time over six weeks, using the specification in each file and the
acceptance tests as your contract.

The project deliberately stays small: three passive sources, optional DNS
brute-force, a scope guard, wildcard handling, and JSONL/TXT output. No
plugins, no configuration files, no extra providers.

## What the finished tool does

1. Asks three public services for known subdomains:
   - crt.sh (certificate transparency)
   - AlienVault OTX (passive DNS)
   - HackerTarget hostsearch
2. Optionally brute-forces names from a small wordlist with DNS.
3. Rejects anything outside the authorized domain.
4. Removes duplicate hosts and records where each one came from.
5. Detects wildcard DNS so random names are not reported as findings.
6. Writes one host per line to TXT or one JSON object per line to JSONL.

Passive collection is on by default. DNS brute-force is **off by default**
because it sends traffic to the target's DNS servers.

## Requirements

- Python 3.11 or newer
- Network access for the passive sources
- Linux, macOS, or Windows

## Setup

```bash
cd SubreconProject
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Verify the package imports:

```bash
python -c "import subrecon; print(subrecon.__file__)"
```

(The `__version__` attribute is added in Week 1.)

## The starting state

Every file in `subrecon/` is a description of what to implement. There is no
working code yet. Running the tests before you start therefore fails during
collection:

```bash
python -m pytest -q
# 7 errors during collection, one per test file
```

That is expected. Each week you implement the modules listed in
`planning.md`, and more tests move from "cannot import" to passing.

Do not edit anything in `tests/`. If a test fails, the code is wrong or
incomplete — not the test.

## Project layout

```
SubreconProject/
├── README.md
├── planning.md                  six-week schedule and rubric
├── ARCHITECTURE.md              how the pieces fit together
├── pyproject.toml               package metadata and dependencies
├── subrecon/
│   ├── __init__.py              package version
│   ├── __main__.py              python -m subrecon entry point
│   ├── exceptions.py            expected error types
│   ├── models.py                Subdomain, Evidence, RunStats, result  (W1)
│   ├── scope.py                 normalization and scope decisions       (W1)
│   ├── http.py                  small shared HTTP client                (W2)
│   ├── dns.py                   async DNS resolution and wildcards      (W2)
│   ├── sources.py               crt.sh, OTX, HackerTarget                (W3)
│   ├── bruteforce.py            wordlist loading and DNS brute-force    (W4)
│   ├── engine.py                the pipeline                            (W5)
│   ├── output.py                JSONL, TXT, summary                     (W6)
│   ├── cli.py                   argument parsing and main()             (W6)
│   └── data/wordlists/subdomains-top100.txt
└── tests/                       acceptance tests — do not edit
    ├── test_models.py       4 tests
    ├── test_scope.py        5 tests
    ├── test_dns.py          2 tests
    ├── test_sources.py      3 tests
    ├── test_bruteforce.py   3 tests
    ├── test_engine.py       2 tests
    └── test_output.py       3 tests
```

22 acceptance tests in total.

## Using the tool

Passive enumeration only:

```bash
subrecon example.com
```

Write results to files and print hostnames:

```bash
subrecon example.com -o out/example --print-hosts
```

Add DNS brute-force with the bundled wordlist:

```bash
subrecon example.com --bruteforce -o out/example
```

Choose sources and restrict scope:

```bash
subrecon example.com --sources crtsh,otx --exclude dev.example.com
```

| Flag | Meaning | Default |
| --- | --- | --- |
| `domain` / `-d` | Target domain | required |
| `--passive` / `--no-passive` | Use the passive sources | on |
| `--bruteforce` / `--no-bruteforce` | Send DNS brute-force queries | off |
| `-w`, `--wordlist` | Extra wordlist (repeatable) | bundled list |
| `--sources` | Comma-separated source names | all three |
| `--include` | Extra in-scope host or suffix (repeatable) | none |
| `--exclude` | Out-of-scope host or glob (repeatable) | none |
| `--concurrency` | Parallel DNS lookups | 100 |
| `--timeout` | HTTP timeout in seconds | 20 |
| `-o`, `--output` | Base path for result files | no files |
| `--format` | `jsonl`, `txt`, or both | both |
| `--keep-wildcards` | Keep hosts flagged as wildcard | off |
| `--print-hosts` | Print hostnames to stdout | off |
| `--list-sources` | Show source names and exit | — |
| `--version` | Show version and exit | — |
| `-v` / `-q` | Debug / quiet logging | normal |

Exit codes: `0` success, `1` unexpected failure, `2` bad input or missing
dependency, `130` interrupted.

## Output formats

TXT — one hostname per line:

```
api.example.com
www.example.com
```

JSONL — one object per line:

```json
{"host":"api.example.com","method":"passive","source":"crtsh","first_seen":"...","last_seen":"...","resolved":true,"addresses":["203.0.113.10"],"cnames":[],"wildcard":false,"evidence":[{"source":"crtsh","detail":"certificate transparency"}]}
```

## Rules

1. Only test domains you own or have written permission to test.
2. Leave brute-force off unless the engagement allows active DNS traffic.
3. Do not edit `tests/`.
4. Keep each module focused on its stated job. No new dependencies without
   asking.
5. Never add a provider that requires an API key. This project stays
   account-free.

## Learning goals

By the end you should be able to:

- validate and normalize untrusted host input;
- run several network requests concurrently and isolate failures;
- resolve DNS asynchronously and reason about wildcard records;
- design a small data model with provenance and de-duplication;
- write deterministic tests around network code using fakes;
- produce machine-readable and human-readable output from one result object.

## Where to start

Read `ARCHITECTURE.md`, then open `subrecon/models.py` and `subrecon/scope.py`.
Week 1 is only those two modules and their nine tests.
