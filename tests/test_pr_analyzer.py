"""
Tests for the PR analyzer.

This module contains tests for the PR analyzer.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add the parent directory to the path so we can import the pr_analysis package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pr_analysis.core.pr_analyzer import PRAnalyzer
from pr_analysis.core.analysis_context import PRAnalysisContext, FileChange
from pr_analysis.rules.base_rule import BaseRule


class TestPRAnalyzer(unittest.TestCase):
    """Tests for the PR analyzer."""
    
    def setUp(self):
        """Set up the test."""
        self.analyzer = PRAnalyzer()
        
    def test_create_context(self):
        """Test creating a context."""
        context = self.analyzer.create_context(
            pr_id="123",
            repo_name="owner/repo",
            base_branch="main",
            head_branch="feature",
        )
        
        self.assertEqual(context.pr_id, "123")
        self.assertEqual(context.repo_name, "owner/repo")
        self.assertEqual(context.base_branch, "main")
        self.assertEqual(context.head_branch, "feature")
        
    def test_add_file_changes(self):
        """Test adding file changes."""
        context = self.analyzer.create_context(
            pr_id="123",
            repo_name="owner/repo",
            base_branch="main",
            head_branch="feature",
        )
        
        file_changes = [
            {
                "filename": "file1.py",
                "status": "added",
                "patch": "+def foo():\n+    return 42",
                "changed_lines": [1, 2],
            },
            {
                "filename": "file2.py",
                "status": "modified",
                "patch": "+def bar():\n+    return 43",
                "changed_lines": [1, 2],
            },
        ]
        
        self.analyzer.add_file_changes(context, file_changes)
        
        self.assertEqual(len(context.file_changes), 2)
        self.assertEqual(context.file_changes["file1.py"].status, "added")
        self.assertEqual(context.file_changes["file2.py"].status, "modified")
        
    def test_analyze(self):
        """Test analyzing a PR."""
        # Create a mock rule
        class MockRule(BaseRule):
            RULE_ID = "mock.rule"
            RULE_NAME = "Mock Rule"
            RULE_DESCRIPTION = "A mock rule for testing"
            RULE_CATEGORY = "mock"
            
            def analyze(self, context):
                return [
                    {
                        "rule_id": self.RULE_ID,
                        "rule_name": self.RULE_NAME,
                        "severity": "warning",
                        "message": "Mock issue",
                        "file": "file1.py",
                        "line": 1,
                    }
                ]
                
        # Register the mock rule
        self.analyzer.rule_engine.register_rule(MockRule)
        
        # Create a context
        context = self.analyzer.create_context(
            pr_id="123",
            repo_name="owner/repo",
            base_branch="main",
            head_branch="feature",
        )
        
        # Add a file change
        file_change = FileChange(
            filename="file1.py",
            status="added",
            patch="+def foo():\n+    return 42",
            changed_lines=[1, 2],
        )
        context.add_file_change(file_change)
        
        # Analyze the PR
        results = self.analyzer.analyze(context)
        
        # Check the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["rule_id"], "mock.rule")
        self.assertEqual(results[0]["severity"], "warning")
        self.assertEqual(results[0]["file"], "file1.py")
        
    def test_generate_report(self):
        """Test generating a report."""
        # Create a context
        context = self.analyzer.create_context(
            pr_id="123",
            repo_name="owner/repo",
            base_branch="main",
            head_branch="feature",
        )
        
        # Generate a report
        report = self.analyzer.generate_report(context, "json")
        
        # Check the report
        self.assertIsInstance(report, str)
        report_data = json.loads(report)
        self.assertEqual(report_data["pr_id"], "123")
        self.assertEqual(report_data["repo_name"], "owner/repo")
        

if __name__ == "__main__":
    unittest.main()

