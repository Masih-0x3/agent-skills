#!/usr/bin/env python3
"""Regression tests for the publication target guard."""

import unittest

from assert_repository_target import repository_from_remote


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


if __name__ == "__main__":
    unittest.main()
