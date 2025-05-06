"""
Tests for the ReportGenerator class.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.pr_static_analysis.reporting.report_generator import ReportGenerator
from src.pr_static_analysis.reporting.utils.config import ReportConfig

class TestReportGenerator(unittest.TestCase):
    """Tests for the ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.report_generator = ReportGenerator()
        self.mock_formatter = MagicMock()
        self.report_generator.register_formatter("test", self.mock_formatter)
        
        # Sample results and metadata
        self.results = [
            {
                "rule_id": "test-001",
                "message": "Test message",
                "severity": "warning",
                "category": "test"
            }
        ]
        self.metadata = {
            "repository": "test/repo",
            "pull_request": 123
        }
        
    def test_register_formatter(self):
        """Test registering a formatter."""
        self.assertIn("test", self.report_generator.formatters)
        self.assertEqual(self.report_generator.formatters["test"], self.mock_formatter)
        
    def test_add_results(self):
        """Test adding results."""
        self.report_generator.add_results(self.results)
        self.assertEqual(self.report_generator.results, self.results)
        
    def test_set_metadata(self):
        """Test setting metadata."""
        self.report_generator.set_metadata(self.metadata)
        self.assertEqual(self.report_generator.metadata, self.metadata)
        
    def test_generate_report(self):
        """Test generating a report."""
        self.report_generator.add_results(self.results)
        self.report_generator.set_metadata(self.metadata)
        self.report_generator.generate_report("test")
        
        # Check that the formatter was called with the correct arguments
        self.mock_formatter.format_report.assert_called_once_with(
            self.results, self.metadata
        )
        
    def test_generate_report_with_config(self):
        """Test generating a report with configuration."""
        self.report_generator.add_results(self.results)
        self.report_generator.set_metadata(self.metadata)
        
        # Create a configuration
        config = ReportConfig()
        config.set("include_summary", True)
        config.set("severity_filter", ["warning"])
        
        # Apply the configuration
        self.report_generator.apply_config(config)
        
        # Generate the report
        self.report_generator.generate_report("test")
        
        # Check that the formatter was called with the correct arguments
        self.mock_formatter.format_report.assert_called_once_with(
            self.results, self.metadata, include_summary=True, include_visualizations=False
        )
        
    def test_filter_results_by_severity(self):
        """Test filtering results by severity."""
        # Add results with different severities
        results = [
            {"rule_id": "test-001", "severity": "warning"},
            {"rule_id": "test-002", "severity": "error"},
            {"rule_id": "test-003", "severity": "warning"}
        ]
        self.report_generator.add_results(results)
        
        # Filter by severity
        filtered = self.report_generator.filter_results_by_severity("warning")
        
        # Check the filtered results
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["rule_id"], "test-001")
        self.assertEqual(filtered[1]["rule_id"], "test-003")
        
    def test_filter_results_by_category(self):
        """Test filtering results by category."""
        # Add results with different categories
        results = [
            {"rule_id": "test-001", "category": "style"},
            {"rule_id": "test-002", "category": "security"},
            {"rule_id": "test-003", "category": "style"}
        ]
        self.report_generator.add_results(results)
        
        # Filter by category
        filtered = self.report_generator.filter_results_by_category("style")
        
        # Check the filtered results
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["rule_id"], "test-001")
        self.assertEqual(filtered[1]["rule_id"], "test-003")
        
    def test_sort_results(self):
        """Test sorting results."""
        # Add results with different rule IDs
        results = [
            {"rule_id": "test-002"},
            {"rule_id": "test-001"},
            {"rule_id": "test-003"}
        ]
        self.report_generator.add_results(results)
        
        # Sort by rule ID
        sorted_results = self.report_generator.sort_results("rule_id")
        
        # Check the sorted results
        self.assertEqual(sorted_results[0]["rule_id"], "test-001")
        self.assertEqual(sorted_results[1]["rule_id"], "test-002")
        self.assertEqual(sorted_results[2]["rule_id"], "test-003")
        
    def test_generate_report_invalid_format(self):
        """Test generating a report with an invalid format."""
        with self.assertRaises(ValueError):
            self.report_generator.generate_report("invalid")

if __name__ == "__main__":
    unittest.main()

