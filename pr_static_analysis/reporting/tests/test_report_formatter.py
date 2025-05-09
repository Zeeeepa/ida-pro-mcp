"""
Unit tests for the report formatter.
"""
import unittest
import json
from pr_static_analysis.reporting.report_formatter import (
    MarkdownReportFormatter,
    HTMLReportFormatter,
    JSONReportFormatter,
    ReportFormatterFactory
)


class TestReportFormatters(unittest.TestCase):
    """Test cases for the report formatters."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample report
        self.report = {
            "pr": {
                "number": 123,
                "title": "Test PR",
                "url": "https://github.com/org/repo/pull/123",
                "base": "main",
                "head": "feature-branch"
            },
            "summary": {
                "error_count": 2,
                "warning_count": 1,
                "info_count": 1,
                "total_count": 4,
                "has_errors": True,
                "has_warnings": True
            },
            "results": [
                {
                    "rule_id": "E1",
                    "message": "Error 1",
                    "severity": "error",
                    "file": "file1.py",
                    "line": 10
                },
                {
                    "rule_id": "E2",
                    "message": "Error 2",
                    "severity": "error",
                    "file": "file2.py",
                    "line": 20
                },
                {
                    "rule_id": "W1",
                    "message": "Warning 1",
                    "severity": "warning",
                    "file": "file3.py",
                    "line": 30
                },
                {
                    "rule_id": "I1",
                    "message": "Info 1",
                    "severity": "info",
                    "file": "file4.py",
                    "line": 40
                }
            ],
            "timestamp": "2023-01-01T12:00:00"
        }
        
        # Create a sample report with no issues
        self.empty_report = {
            "pr": {
                "number": 123,
                "title": "Test PR",
                "url": "https://github.com/org/repo/pull/123",
                "base": "main",
                "head": "feature-branch"
            },
            "summary": {
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0,
                "total_count": 0,
                "has_errors": False,
                "has_warnings": False
            },
            "results": [],
            "timestamp": "2023-01-01T12:00:00"
        }
    
    def test_markdown_formatter(self):
        """Test the Markdown formatter."""
        formatter = MarkdownReportFormatter()
        markdown = formatter.format_report(self.report)
        
        # Check that the markdown contains expected elements
        self.assertIn("# PR Analysis Report for #123", markdown)
        self.assertIn("**PR:** [Test PR](https://github.com/org/repo/pull/123)", markdown)
        self.assertIn("**Base:** `main`", markdown)
        self.assertIn("**Head:** `feature-branch`", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("- **Errors:** 2", markdown)
        self.assertIn("- **Warnings:** 1", markdown)
        self.assertIn("- **Info:** 1", markdown)
        self.assertIn("- **Total:** 4", markdown)
        self.assertIn("## Issues", markdown)
        self.assertIn(":x: E1: Error 1", markdown)
        self.assertIn("**File:** `file1.py`", markdown)
        self.assertIn("**Line:** 10", markdown)
        self.assertIn(":warning: W1: Warning 1", markdown)
        self.assertIn(":information_source: I1: Info 1", markdown)
    
    def test_markdown_formatter_empty(self):
        """Test the Markdown formatter with no issues."""
        formatter = MarkdownReportFormatter()
        markdown = formatter.format_report(self.empty_report)
        
        # Check that the markdown contains expected elements
        self.assertIn("# PR Analysis Report for #123", markdown)
        self.assertIn("**PR:** [Test PR](https://github.com/org/repo/pull/123)", markdown)
        self.assertIn("**Base:** `main`", markdown)
        self.assertIn("**Head:** `feature-branch`", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("- **Errors:** 0", markdown)
        self.assertIn("- **Warnings:** 0", markdown)
        self.assertIn("- **Info:** 0", markdown)
        self.assertIn("- **Total:** 0", markdown)
        self.assertIn("No issues found! :white_check_mark:", markdown)
    
    def test_html_formatter(self):
        """Test the HTML formatter."""
        formatter = HTMLReportFormatter()
        html = formatter.format_report(self.report)
        
        # Check that the HTML contains expected elements
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>PR Analysis Report", html)
        self.assertIn("<h1>PR Analysis Report for #123</h1>", html)
        self.assertIn("<a href=\"https://github.com/org/repo/pull/123\">Test PR</a>", html)
        self.assertIn("<code>main</code>", html)
        self.assertIn("<code>feature-branch</code>", html)
        self.assertIn("<h2>Summary</h2>", html)
        self.assertIn("<h3>Errors</h3>", html)
        self.assertIn("<p>2</p>", html)
        self.assertIn("<h3>Warnings</h3>", html)
        self.assertIn("<p>1</p>", html)
        self.assertIn("<h3>Info</h3>", html)
        self.assertIn("<p>1</p>", html)
        self.assertIn("<h3>Total</h3>", html)
        self.assertIn("<p>4</p>", html)
        self.assertIn("<h2>Issues</h2>", html)
        self.assertIn("E1: Error 1", html)
        self.assertIn("file1.py", html)
        self.assertIn("W1: Warning 1", html)
        self.assertIn("I1: Info 1", html)
    
    def test_html_formatter_empty(self):
        """Test the HTML formatter with no issues."""
        formatter = HTMLReportFormatter()
        html = formatter.format_report(self.empty_report)
        
        # Check that the HTML contains expected elements
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>PR Analysis Report", html)
        self.assertIn("<h1>PR Analysis Report for #123</h1>", html)
        self.assertIn("<a href=\"https://github.com/org/repo/pull/123\">Test PR</a>", html)
        self.assertIn("<code>main</code>", html)
        self.assertIn("<code>feature-branch</code>", html)
        self.assertIn("<h2>Summary</h2>", html)
        self.assertIn("<h3>Errors</h3>", html)
        self.assertIn("<p>0</p>", html)
        self.assertIn("<h3>Warnings</h3>", html)
        self.assertIn("<p>0</p>", html)
        self.assertIn("<h3>Info</h3>", html)
        self.assertIn("<p>0</p>", html)
        self.assertIn("<h3>Total</h3>", html)
        self.assertIn("<p>0</p>", html)
        self.assertIn("<p>No issues found! ✅</p>", html)
    
    def test_json_formatter(self):
        """Test the JSON formatter."""
        formatter = JSONReportFormatter()
        json_str = formatter.format_report(self.report)
        
        # Parse the JSON and check that it matches the original report
        parsed = json.loads(json_str)
        self.assertEqual(parsed, self.report)
    
    def test_formatter_factory(self):
        """Test the formatter factory."""
        # Test creating a Markdown formatter
        formatter = ReportFormatterFactory.create_formatter("markdown")
        self.assertIsInstance(formatter, MarkdownReportFormatter)
        
        # Test creating an HTML formatter
        formatter = ReportFormatterFactory.create_formatter("html")
        self.assertIsInstance(formatter, HTMLReportFormatter)
        
        # Test creating a JSON formatter
        formatter = ReportFormatterFactory.create_formatter("json")
        self.assertIsInstance(formatter, JSONReportFormatter)
        
        # Test creating a formatter with an unsupported format
        with self.assertRaises(ValueError):
            ReportFormatterFactory.create_formatter("unsupported")


if __name__ == "__main__":
    unittest.main()

