#!/usr/bin/env python3
"""Run the decomposer's dependency-light function tests without pytest."""

from __future__ import annotations

import importlib.util
import sys
import traceback

from skilllib import ROOT


def main() -> int:
    tests = ROOT / "skills" / "project-task-decomposer" / "tests"
    failed = 0
    count = 0
    for path in sorted(tests.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            print(f"ERROR unable to load {path}")
            failed += 1
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            for name in sorted(dir(module)):
                if name.startswith("test_") and callable(getattr(module, name)):
                    count += 1
                    getattr(module, name)()
                    print(f"OK {path.name}::{name}")
        except Exception:
            failed += 1
            traceback.print_exc()
    if count == 0:
        print("ERROR no tests found")
        return 1
    print(f"Ran {count} decomposer tests; failures: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
