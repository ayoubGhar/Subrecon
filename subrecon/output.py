"""
MODULE: output.py — WEEK 6

PURPOSE
    Write results to JSONL or plain text and render a short human-readable
    summary.

SPEC
    ARCHITECTURE.md section 10 (output). Acceptance: tests/test_output.py.

WHAT TO IMPLEMENT
    write_jsonl(result, path) -> Path
      Create parent directories, open the path as UTF-8, and write one compact
      JSON object per line using each Subdomain.to_dict(). Return the path.

    write_txt(result, path) -> Path
      Create parent directories, open the path as UTF-8, and write one hostname
      per line. Return the path.

    write_outputs(result, base_path, formats=("jsonl", "txt")) -> list of Path
      For each requested format, write base_path plus ".jsonl" or ".txt".
      Reject any other format with ValueError. Return the written paths.

    render_summary(result) -> str
      Build a multi-line summary containing:
        - the heading "Subrecon summary";
        - target, duration with two decimals and an "s" suffix;
        - discovered, passive, active, resolved counts;
        - wildcard with " dropped", out-of-scope with " ignored";
        - "(no hosts discovered)" when the list is empty.
      Use exactly these labels, two leading spaces, and this alignment:
        Subrecon summary
          target       : <domain>
          duration     : <0.00>s
          discovered   : <n>
          passive      : <n>
          active       : <n>
          resolved     : <n>
          wildcard     : <n> dropped
          out of scope : <n> ignored
      Join with newlines and return the text.

CONSTRAINTS
    Output functions do no network access and do not mutate the result.
"""