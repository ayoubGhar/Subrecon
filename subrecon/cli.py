"""
MODULE: cli.py — WEEK 6

PURPOSE
    Parse command-line arguments, choose the passive sources, run one
    enumeration, optionally write files, and return a stable exit code.

SPEC
    ARCHITECTURE.md section 10 (CLI and output). Acceptance: the demo in
    planning.md.

WHAT TO IMPLEMENT
    build_parser() -> argparse.ArgumentParser
      Program "subrecon" with a short description and an authorization epilog.
      Options:
        domain (positional, optional) or -d/--domain
        --passive / --no-passive          default on
        --bruteforce / --no-bruteforce    default off (active traffic is opt-in)
        -w, --wordlist FILE                repeatable
        --sources LIST                     comma-separated names, default all
        --include HOST                     repeatable
        --exclude HOST                     repeatable
        --concurrency N                    default 100
        --timeout SECONDS                  default 20
        -o, --output PATH                  base path, no extension
        --format LIST                      jsonl,txt (default both)
        --keep-wildcards                   keep wildcard-classified hosts
        --print-hosts                      print hostnames to stdout
        --list-sources                     print known sources and exit
        --version                          print the package version
        -v, --verbose                      debug logging
        -q, --quiet                        errors only

    main(argv=None) -> int
      1. Parse arguments. Handle --list-sources and return 0.
      2. Resolve the domain from the option or positional value; normalize it.
         A missing or invalid domain prints an error and returns 2.
      3. Resolve the source names. Unknown names print an error and return 2.
      4. Build HttpClient(timeout=...) and Resolver().
      5. Load words only when brute-force is enabled:
         load_words(args.wordlist or []).
      6. Run enumerate_domain with the http client, resolver, selected source
         functions, words, include/exclude, concurrency and keep_wildcards.
      7. Always close the HTTP client in the same event loop as the run: put
         the engine call and aclose in one async helper and use a single
         asyncio.run. Do not reuse the client after its loop closes.
      8. If an output path is given, call write_outputs with the parsed formats;
         a write failure prints an error and returns 1.
      9. Print render_summary to stderr. Print bare hosts to stdout when
         print_hosts is enabled. Return 0.
      Catch KeyboardInterrupt and return 130, MissingDependency and return 2,
      and any other unexpected exception: print a concise error and return 1.

CONSTRAINTS
    Keep stdout clean: the summary goes to stderr.
"""