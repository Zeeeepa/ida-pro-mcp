"""
Tests for the report formatters.
"""

import unittest
import json
from src.pr_static_analysis.reporting.formatters.markdown_formatter import MarkdownFormatter
from src.pr_static_analysis.reporting.formatters.html_formatter import HTMLFormatter
from src.pr_static_analysis.reporting.formatters.json_formatter import JSONFormatter
from src.pr_static_analysis.reporting.formatters.text_formatter import TextFormatter

class TestFormatters(unittest.TestCase):
    """Tests for the report formatters."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample results and metadata
        self.results = [
            {
                "rule_id": "test-001",
                "message": "Test message 1",
                "file_path": "src/test.py",
                "line": 10,
                "severity": "warning",
                "category": "style"
            },
            {
                "rule_id": "test-002",
                "message": "Test message 2",
                "file_path": "src/test.py",
                "line": 20,
                "severity": "error",
                "category": "security"
            }
        ]
        self.metadata = {
            "repository": "test/repo",
            "pull_request": 123
        }
        
        # Create formatters
        self.markdown_formatter = MarkdownFormatter()
        self.html_formatter = HTMLFormatter()
        self.json_formatter = JSONFormatter()
        self.text_formatter = TextFormatter()
        
    def test_markdown_formatter(self):
        """Test the Markdown formatter."""
        report = self.markdown_formatter.format_report(self.results, self.metadata)
        
        # Check that the report contains expected elements
        self.assertIn("# PR Analysis Report", report)
        self.assertIn("## Metadata", report)
        self.assertIn("repository", report)
        self.assertIn("test/repo", report)
        self.assertIn("## Summary", report)
        self.assertIn("warning", report)
        self.assertIn("error", report)
        self.assertIn("### test-001", report)
        self.assertIn("### test-002", report)
        self.assertIn("Test message 1", report)
        self.assertIn("Test message 2", report)
        self.assertIn("src/test.py", report)
        
    def test_html_formatter(self):
        """Test the HTML formatter."""
        report = self.html_formatter.format_report(self.results, self.metadata)
        
        # Check that the report contains expected elements
        self.assertIn("<html>", report)
        self.assertIn("<title>PR Analysis Report</title>", report)
        self.assertIn("<h1>PR Analysis Report</h1>", report)
        self.assertIn("<h2>Metadata</h2>", report)
        self.assertIn("repository", report)
        self.assertIn("test/repo", report)
        self.assertIn("<h2>Summary</h2>", report)
        self.assertIn("warning", report)
        self.assertIn("error", report)
        self.assertIn("test-001", report)
        self.assertIn("test-002", report)
        self.assertIn("Test message 1", report)
        self.assertIn("Test message 2", report)
        self.assertIn("src/test.py", report)
        
    def test_json_formatter(self):
        """Test the JSON formatter."""
        report = self.json_formatter.format_report(self.results, self.metadata)
        
        # Parse the JSON report
        report_dict = json.loads(report)
        
        # Check the structure
        self.assertIn("metadata", report_dict)
        self.assertIn("results", report_dict)
        self.assertIn("summary", report_dict)
        
        # Check the metadata
        self.assertEqual(report_dict["metadata"]["repository"], "test/repo")
        self.assertEqual(report_dict["metadata"]["pull_request"], 123)
        
        # Check the results
        self.assertEqual(len(report_dict["results"]), 2)
        self.assertEqual(report_dict["results"][0]["rule_id"], "test-001")
        self.assertEqual(report_dict["results"][1]["rule_id"], "test-002")
        
        # Check the summary
        self.assertEqual(report_dict["summary"]["total"], 2)
        self.assertEqual(report_dict["summary"]["by_severity"]["warning"], 1)
        self.assertEqual(report_dict["summary"]["by_severity"]["error"], 1)
        
    def test_text_formatter(self):
        """Test the text formatter."""
        report = self.text_formatter.format_report(self.results, self.metadata)
        
        # Check that the report contains expected elements
        self.assertIn("PR ANALYSIS REPORT", report)
        self.assertIn("METADATA", report)
        self.assertIn("repository: test/repo", report)
        self.assertIn("pull_request: 123", report)
        self.assertIn("SUMMARY", report)
        self.assertIn("Warning: 1 issue(s)", report)
        self.assertIn("Error: 1 issue(s)", report)
        self.assertIn("test-001", report)
        self.assertIn("test-002", report)
        self.assertIn("Message: Test message 1", report)
        self.assertIn("Message: Test message 2", report)
        self.assertIn("Location: in src/test.py at line 10", report)
        self.assertIn("Location: in src/test.py at line 20", report)

if __name__ == "__main__":
    unittest.main()

