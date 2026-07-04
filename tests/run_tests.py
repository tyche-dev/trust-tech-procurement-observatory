#!/usr/bin/env python3
"""Dependency-free test runner (no pytest required).

Discovers every `test_*` function in tests/test_*.py, runs it, and reports pass/fail.
Also usable under pytest if it is installed. Exit code is non-zero on any failure, so it
works as a CI gate. Run: python3 tests/run_tests.py
"""
import importlib.util
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    total = failed = 0
    for f in sorted(HERE.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in sorted(dir(mod)):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            total += 1
            try:
                fn()
                print(f"  PASS {f.name}::{name}")
            except Exception:
                failed += 1
                print(f"  FAIL {f.name}::{name}")
                traceback.print_exc()
    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
