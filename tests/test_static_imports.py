#!/usr/bin/env python3
"""
Static analysis test for import issues in the ida-pro-mcp package.
This test uses pylint to check for import-related issues.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path


class TestStaticImports(unittest.TestCase):
    """Test for import-related issues using static analysis."""

    def setUp(self):
        """Set up the test environment."""
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"

    def test_pylint_imports(self):
        """Test for import-related issues using pylint."""
        # Check if pylint is installed
        try:
            subprocess.run(
                [sys.executable, "-m", "pylint", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("pylint is not installed")

        # Run pylint with import-related checks only
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pylint",
                "--disable=all",
                "--enable=import-error,import-self,reimported,relative-import,deprecated-module",
                "--ignore=__pycache__",
                str(self.src_dir)
            ],
            capture_output=True,
            text=True
        )

        # If pylint found issues, the test fails
        if result.returncode != 0:
            self.fail(f"Pylint found import issues:\n{result.stdout}\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()

