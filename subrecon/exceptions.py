"""
MODULE: exceptions.py

PURPOSE
    Typed expected errors so the CLI can map failures to exit codes without
    catching broad exception classes.

WHAT TO IMPLEMENT
    class SubreconError(Exception)
      Base class for expected failures.

    class ConfigError(SubreconError)
      Invalid command-line input. The CLI maps it to exit code 2.

    class MissingDependency(SubreconError)
      httpx or dnspython is not installed. The message must include an install
      hint. The CLI maps it to exit code 2.
"""