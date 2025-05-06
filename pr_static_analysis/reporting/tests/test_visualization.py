"""
Unit tests for the visualization components.
"""
import unittest
import base64
from pr_static_analysis.reporting.visualization import ReportVisualizer


class TestReportVisualizer(unittest.TestCase):
    """Test cases for the ReportVisualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = ReportVisualizer()
        
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
    
    def test_generate_summary_chart(self):
        """Test generating a summary chart."""
        chart = self.visualizer.generate_summary_chart(self.report)
        
        # Check that the chart is a base64 encoded PNG
        self._assert_is_base64_png(chart)
    
    def test_generate_summary_chart_empty(self):
        """Test generating a summary chart with no issues."""
        chart = self.visualizer.generate_summary_chart(self.empty_report)
        
        # Check that the chart is a base64 encoded PNG
        self._assert_is_base64_png(chart)
    
    def test_generate_severity_distribution(self):
        """Test generating a severity distribution chart."""
        chart = self.visualizer.generate_severity_distribution(self.report)
        
        # Check that the chart is a base64 encoded PNG
        self._assert_is_base64_png(chart)
    
    def test_generate_severity_distribution_empty(self):
        """Test generating a severity distribution chart with no issues."""
        chart = self.visualizer.generate_severity_distribution(self.empty_report)
        
        # Check that the chart is a base64 encoded PNG
        self._assert_is_base64_png(chart)
    
    def test_generate_file_heatmap(self):
        """Test generating a file heatmap."""
        chart = self.visualizer.generate_file_heatmap(self.report)
        
        # Check that the chart is a base64 encoded PNG
        self._assert_is_base64_png(chart)
    
    def test_generate_file_heatmap_empty(self):
        """Test generating a file heatmap with no issues."""
        chart = self.visualizer.generate_file_heatmap(self.empty_report)
        
        # Check that the chart is a base64 encoded PNG
        self._assert_is_base64_png(chart)
    
    def test_shorten_path(self):
        """Test shortening a file path."""
        # Test a short path
        path = "file.py"
        shortened = self.visualizer._shorten_path(path, max_length=40)
        self.assertEqual(shortened, "file.py")
        
        # Test a long path
        path = "very/long/path/with/many/directories/file.py"
        shortened = self.visualizer._shorten_path(path, max_length=40)
        self.assertLessEqual(len(shortened), 40)
        self.assertIn("...", shortened)
        
        # Test a path with a very long filename
        path = "very_long_filename_that_exceeds_the_maximum_length.py"
        shortened = self.visualizer._shorten_path(path, max_length=40)
        self.assertLessEqual(len(shortened), 40)
        self.assertIn("...", shortened)
    
    def _assert_is_base64_png(self, data):
        """Assert that the data is a base64 encoded PNG."""
        # Check that the data is a string
        self.assertIsInstance(data, str)
        
        # Check that the data is not empty
        self.assertTrue(data)
        
        # Check that the data is valid base64
        try:
            decoded = base64.b64decode(data)
        except Exception:
            self.fail("Data is not valid base64")
        
        # Check that the decoded data starts with the PNG signature
        self.assertTrue(decoded.startswith(b'\x89PNG\r\n\x1a\n'))


if __name__ == "__main__":
    unittest.main()

