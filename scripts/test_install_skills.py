#!/usr/bin/env python3
"""Tests for cross-platform installer behavior."""

import unittest

from install_skills import retry_transient_lock


class RetryTransientLockTests(unittest.TestCase):
    def test_retries_permission_error(self) -> None:
        calls = 0

        def operation() -> str:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise PermissionError("temporarily locked")
            return "done"

        self.assertEqual(retry_transient_lock(operation, attempts=3), "done")
        self.assertEqual(calls, 3)

    def test_does_not_retry_other_errors(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "permanent"):
            retry_transient_lock(lambda: (_ for _ in ()).throw(RuntimeError("permanent")))


if __name__ == "__main__":
    unittest.main()
