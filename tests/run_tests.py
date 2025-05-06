#!/usr/bin/env python3
"""
Test runner for the ida-pro-mcp package.
"""

import os
import sys
import unittest
from pathlib import Path


def run_tests():
    """Run all tests for the ida-pro-mcp package."""
    # Add the project root and src directory to the path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))

    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir=Path(__file__).parent, pattern="test_*.py")
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
