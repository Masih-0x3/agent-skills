#!/usr/bin/env python3
"""Behavior tests for the curated Lovable export profile."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPORTER = ROOT / "scripts" / "export_lovable.py"
PROFILE = ROOT / "catalog" / "lovable-general-use.json"

# Independent contract: changing the profile requires an intentional test update.
EXPECTED_NAMES = {
    "ab-testing",
    "ai-seo",
    "animation-vocabulary",
    "apple-design",
    "ask-sonner",
    "better-colors",
    "better-typography",
    "better-ui",
    "codebase-design",
    "content-strategy",
    "copy-editing",
    "copywriting",
    "cro",
    "domain-modeling",
    "emil-design-eng",
    "find-animation-opportunities",
    "high-end-visual-design",
    "minimalist-ui",
    "onboarding",
    "paywalls",
    "pick-ui-library",
    "pricing",
    "product-marketing",
    "schema",
    "signup",
    "site-architecture",
    "tdd",
    "transitions-dev",
}


class LovableExportTests(unittest.TestCase):
    def run_export(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(EXPORTER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_profile_is_explicit_and_excludes_operator_skills(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertEqual(profile["schema_version"], 1)
        self.assertIn("28-skill", profile["description"])
        self.assertEqual(len(profile["skills"]), 28)
        self.assertEqual(set(profile["skills"]), EXPECTED_NAMES)
        self.assertNotIn("computer-use", profile["skills"])
        self.assertNotIn("playwright", profile["skills"])
        self.assertNotIn("pentest-tools", profile["skills"])
        self.assertNotIn("compact-landing", profile["skills"])
        self.assertNotIn("transitions-polish", profile["skills"])
        self.assertTrue(profile["selection_rules"])
        self.assertTrue(profile["excluded_examples"])

    def test_invalid_profile_names_fail_before_path_resolution(self) -> None:
        for profile_name in ("../general-use", "general-use/../general-use", "general_use", "General-Use"):
            with self.subTest(profile_name=profile_name):
                result = self.run_export("--profile", profile_name)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid profile name", result.stderr)

    def test_profile_exports_are_byte_identical_and_index_hashes_each_zip(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for directory in (first, second):
                result = self.run_export("--profile", "general-use", "--output", directory, "--check")
                self.assertEqual(result.returncode, 0, result.stderr)
            first_path, second_path = Path(first), Path(second)
            first_index = (first_path / "index.json").read_bytes()
            second_index = (second_path / "index.json").read_bytes()
            self.assertEqual(first_index, second_index)
            first_data = json.loads(first_index)
            for item in first_data["skills"]:
                first_zip = (first_path / item["zip"]).read_bytes()
                second_zip = (second_path / item["zip"]).read_bytes()
                self.assertEqual(first_zip, second_zip, item["name"])
                self.assertEqual(hashlib.sha256(first_zip).hexdigest(), item["zip_sha256"])

    def test_profile_export_writes_index_manifests_and_one_zip_per_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_export("--profile", "general-use", "--output", directory, "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
            output = Path(directory)
            self.assertEqual(
                {path.stem for path in output.glob("*.zip")},
                EXPECTED_NAMES,
            )
            self.assertEqual(
                {path.stem.removesuffix(".manifest") for path in output.glob("*.manifest.json")},
                EXPECTED_NAMES,
            )
            index = json.loads((output / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["profile"], "general-use")
            self.assertEqual({item["name"] for item in index["skills"]}, EXPECTED_NAMES)
            self.assertNotIn("computer-use", {item["name"] for item in index["skills"]})
            with zipfile.ZipFile(output / "ask-sonner.zip") as archive:
                self.assertEqual(archive.namelist(), ["ask-sonner/API.md", "ask-sonner/SKILL.md"])

    def test_explicit_skill_export_behavior_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_export("animation-vocabulary", "--output", directory, "--check")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(directory) / "animation-vocabulary.zip").is_file())
            self.assertFalse((Path(directory) / "computer-use.zip").exists())


if __name__ == "__main__":
    unittest.main()
