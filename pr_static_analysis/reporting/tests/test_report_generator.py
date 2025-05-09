"""
Unit tests for the report generator.
"""
import unittest
from unittest.mock import MagicMock
from datetime import datetime

from pr_static_analysis.reporting.report_generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        
        # Create mock PR context
        self.pr_context = MagicMock()
        self.pr_context.number = 123
        self.pr_context.title = "Test PR"
        self.pr_context.html_url = "https://github.com/org/repo/pull/123"
        self.pr_context.base.ref = "main"
        self.pr_context.head.ref = "feature-branch"
        
        # Create mock results
        self.results = []
        for i in range(3):
            result = MagicMock()
            result.severity = "error"
            result.to_dict.return_value = {
                "rule_id": f"E{i+1}",
                "message": f"Error {i+1}",
                "severity": "error",
                "file": f"file{i+1}.py",
                "line": i+1
            }
            self.results.append(result)
            
        for i in range(2):
            result = MagicMock()
            result.severity = "warning"
            result.to_dict.return_value = {
                "rule_id": f"W{i+1}",
                "message": f"Warning {i+1}",
                "severity": "warning",
                "file": f"file{i+3+1}.py",
                "line": i+4
            }
            self.results.append(result)
            
        for i in range(1):
            result = MagicMock()
            result.severity = "info"
            result.to_dict.return_value = {
                "rule_id": f"I{i+1}",
                "message": f"Info {i+1}",
                "severity": "info",
                "file": f"file{i+5+1}.py",
                "line": i+6
            }
            self.results.append(result)
    
    def test_generate_report(self):
        """Test generating a report."""
        report = self.generator.generate_report(self.results, self.pr_context)
        
        # Check PR info
        self.assertEqual(report["pr"]["number"], 123)
        self.assertEqual(report["pr"]["title"], "Test PR")
        self.assertEqual(report["pr"]["url"], "https://github.com/org/repo/pull/123")
        self.assertEqual(report["pr"]["base"], "main")
        self.assertEqual(report["pr"]["head"], "feature-branch")
        
        # Check summary
        self.assertEqual(report["summary"]["error_count"], 3)
        self.assertEqual(report["summary"]["warning_count"], 2)
        self.assertEqual(report["summary"]["info_count"], 1)
        self.assertEqual(report["summary"]["total_count"], 6)
        self.assertTrue(report["summary"]["has_errors"])
        self.assertTrue(report["summary"]["has_warnings"])
        
        # Check results
        self.assertEqual(len(report["results"]), 6)
        
        # Check timestamp
        self.assertIsNotNone(report["timestamp"])
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(report["timestamp"])
        except ValueError:
            self.fail("Timestamp is not in ISO format")
    
    def test_generate_summary(self):
        """Test generating a summary."""
        summary = self.generator._generate_summary(self.results)
        
        self.assertEqual(summary["error_count"], 3)
        self.assertEqual(summary["warning_count"], 2)
        self.assertEqual(summary["info_count"], 1)
        self.assertEqual(summary["total_count"], 6)
        self.assertTrue(summary["has_errors"])
        self.assertTrue(summary["has_warnings"])
    
    def test_get_timestamp(self):
        """Test getting a timestamp."""
        timestamp = self.generator._get_timestamp()
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            self.fail("Timestamp is not in ISO format")


if __name__ == "__main__":
    unittest.main()

