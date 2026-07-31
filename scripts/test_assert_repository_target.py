#!/usr/bin/env python3
"""Regression tests for the publication target guard."""

import unittest

from assert_repository_target import repository_from_remote
from skilllib import load_source_lock, source_for


class RepositoryFromRemoteTests(unittest.TestCase):
    def test_accepts_exact_github_https_remote(self) -> None:
        self.assertEqual(
            repository_from_remote("https://github.com/Masih-0x3/agent-skills.git"),
            "Masih-0x3/agent-skills",
        )

    def test_accepts_exact_github_scp_remote(self) -> None:
        self.assertEqual(
            repository_from_remote("git@github.com:Masih-0x3/agent-skills.git"),
            "Masih-0x3/agent-skills",
        )

    def test_rejects_lookalike_hostname(self) -> None:
        self.assertEqual(
            repository_from_remote("https://notgithub.com/Masih-0x3/agent-skills"),
            "",
        )

    def test_rejects_github_subdomain(self) -> None:
        self.assertEqual(
            repository_from_remote("https://github.com.evil.test/Masih-0x3/agent-skills"),
            "",
        )

    def test_rejects_extra_path_segments(self) -> None:
        self.assertEqual(
            repository_from_remote("https://github.com/extra/Masih-0x3/agent-skills"),
            "",
        )


class SourceProvenanceTests(unittest.TestCase):
    def test_rejects_skill_missing_from_baseline(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicit immutable source mapping"):
            source_for("not-in-the-baseline", load_source_lock())


if __name__ == "__main__":
    unittest.main()
