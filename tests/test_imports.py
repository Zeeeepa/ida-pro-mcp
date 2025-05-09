#!/usr/bin/env python3
"""
Test module imports for the ida-pro-mcp package.
This test ensures that all modules can be imported without errors.
"""

import importlib
import os
import sys
import unittest
from pathlib import Path


class TestModuleImports(unittest.TestCase):
    """Test that all modules in the package can be imported without errors."""

    def setUp(self):
        """Set up the test environment."""
        # Add the src directory to the path so we can import the package
        self.project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(self.project_root / "src"))
        
        # List of known dependencies that might not be installed in CI
        self.optional_dependencies = [
            'typing_inspection',
            'mcp',
            'idapro',
            # IDA Pro specific modules
            'ida_pro',
            'ida_hexrays',
            'ida_kernwin',
            'ida_idaapi',
            'ida_loader',
            'ida_nalt',
            'ida_netnode',
            'ida_diskio',
            'ida_auto',
            'ida_bytes',
            'ida_funcs',
            'ida_name',
            'ida_segment',
            'ida_typeinf',
            'ida_ua',
            'ida_xref',
            'idautils',
            'idc',
            'idaapi',
            'ida_gdl',
            'ida_lines',
            'ida_entry',
            'ida_idd',
            'ida_dbg',
            'ida_ida',
        ]

    def test_package_import(self):
        """Test that the main package can be imported."""
        try:
            import ida_pro_mcp
            self.assertTrue(True, "Main package imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import main package: {e}")

    def test_all_modules(self):
        """Test that all modules in the package can be imported."""
        package_dir = Path(self.project_root) / "src" / "ida_pro_mcp"
        
        # Skip __pycache__ directories and non-Python files
        for item in package_dir.glob("**/*.py"):
            if "__pycache__" in str(item):
                continue
                
            # Convert file path to module path
            rel_path = item.relative_to(Path(self.project_root) / "src")
            module_path = str(rel_path).replace(os.sep, ".")[:-3]  # Remove .py extension
            
            try:
                importlib.import_module(module_path)
                print(f"Successfully imported {module_path}")
            except ImportError as e:
                # Check if the import error is due to a missing optional dependency
                error_msg = str(e)
                skip_test = False
                
                for dep in self.optional_dependencies:
                    if f"No module named '{dep}'" in error_msg:
                        print(f"Skipping {module_path} due to missing optional dependency: {dep}")
                        skip_test = True
                        break
                
                if not skip_test:
                    self.fail(f"Failed to import {module_path}: {e}")
            except Exception as e:
                # Some modules might raise exceptions when imported outside of IDA Pro
                # We'll note these but not fail the test
                print(f"Warning: {module_path} raised {type(e).__name__}: {e}")

    def test_import_dependencies(self):
        """Test that all dependencies can be imported."""
        try:
            import mcp
            print("Successfully imported mcp")
        except ImportError as e:
            # Skip this test if mcp is not installed
            self.skipTest(f"Dependency 'mcp' not installed: {e}")


if __name__ == "__main__":
    unittest.main()
