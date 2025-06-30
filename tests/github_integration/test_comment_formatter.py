"""
Unit tests for the GitHubCommentFormatter class.
"""

import unittest
from ida_pro_mcp.github_integration.comment_formatter import GitHubCommentFormatter


class TestGitHubCommentFormatter(unittest.TestCase):
    """
    Test cases for the GitHubCommentFormatter class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.formatter = GitHubCommentFormatter()
    
    def test_format_results_empty(self):
        """
        Test formatting empty results.
        """
        results = {}
        comment = self.formatter.format_results(results)
        self.assertIn("No issues found", comment)
    
    def test_format_results_no_issues(self):
        """
        Test formatting results with no issues.
        """
        results = {"issues": []}
        comment = self.formatter.format_results(results)
        self.assertIn("No issues found", comment)
    
    def test_format_results_with_issues(self):
        """
        Test formatting results with issues.
        """
        results = {
            "issues": [
                {
                    "severity": "error",
                    "message": "Test error",
                    "file": "test.py",
                    "line": 10
                },
                {
                    "severity": "warning",
                    "message": "Test warning",
                    "file": "test.py",
                    "line": 20
                },
                {
                    "severity": "info",
                    "message": "Test info"
                }
            ]
        }
        
        comment = self.formatter.format_results(results)
        
        # Check summary
        self.assertIn("Total issues: 3", comment)
        self.assertIn("Errors: 1", comment)
        self.assertIn("Warnings: 1", comment)
        self.assertIn("Info: 1", comment)
        
        # Check details
        self.assertIn("### Errors", comment)
        self.assertIn("**Test error**", comment)
        self.assertIn("`test.py`", comment)
        self.assertIn("line 10", comment)
        
        self.assertIn("### Warnings", comment)
        self.assertIn("**Test warning**", comment)
        self.assertIn("line 20", comment)
        
        self.assertIn("### Info", comment)
        self.assertIn("**Test info**", comment)
    
    def test_format_results_with_code(self):
        """
        Test formatting issues with code identifiers.
        """
        results = {
            "issues": [
                {
                    "severity": "error",
                    "message": "Test error",
                    "code": "E001",
                    "file": "test.py",
                    "line": 10
                }
            ]
        }
        
        comment = self.formatter.format_results(results)
        self.assertIn("**[E001]** Test error", comment)
    
    def test_format_results_with_column(self):
        """
        Test formatting issues with column information.
        """
        results = {
            "issues": [
                {
                    "severity": "error",
                    "message": "Test error",
                    "file": "test.py",
                    "line": 10,
                    "column": 5
                }
            ]
        }
        
        comment = self.formatter.format_results(results)
        self.assertIn("line 10, column 5", comment)
    
    def test_format_results_with_recommendations(self):
        """
        Test formatting results with recommendations.
        """
        results = {
            "issues": [
                {
                    "severity": "error",
                    "message": "Test error"
                }
            ],
            "recommendations": [
                "Fix the error",
                "Add more tests"
            ]
        }
        
        comment = self.formatter.format_results(results)
        self.assertIn("### Recommendations", comment)
        self.assertIn("- Fix the error", comment)
        self.assertIn("- Add more tests", comment)
    
    def test_format_results_with_summary(self):
        """
        Test formatting results with custom summary.
        """
        results = {
            "issues": [
                {
                    "severity": "error",
                    "message": "Test error"
                }
            ],
            "summary": {
                "total_files": 10,
                "analyzed_files": 8,
                "execution_time": 1.23
            }
        }
        
        comment = self.formatter.format_results(results)
        self.assertIn("Files analyzed: 8/10", comment)
        self.assertIn("Execution time: 1.23s", comment)
    
    def test_format_error(self):
        """
        Test formatting an error message.
        """
        error = "Something went wrong"
        comment = self.formatter.format_error(error)
        self.assertIn("❌ PR Static Analysis Error", comment)
        self.assertIn("Something went wrong", comment)
    
    def test_format_summary_no_issues(self):
        """
        Test formatting a summary with no issues.
        """
        results = {"issues": []}
        summary = self.formatter.format_summary(results)
        self.assertEqual(summary, "✅ No issues found")
    
    def test_format_summary_with_errors(self):
        """
        Test formatting a summary with errors.
        """
        results = {
            "issues": [
                {"severity": "error", "message": "Error 1"},
                {"severity": "error", "message": "Error 2"},
                {"severity": "warning", "message": "Warning 1"}
            ]
        }
        
        summary = self.formatter.format_summary(results)
        self.assertIn("❌ 2 errors", summary)
        self.assertIn("⚠️ 1 warning", summary)
    
    def test_format_summary_with_warnings_only(self):
        """
        Test formatting a summary with warnings only.
        """
        results = {
            "issues": [
                {"severity": "warning", "message": "Warning 1"},
                {"severity": "warning", "message": "Warning 2"}
            ]
        }
        
        summary = self.formatter.format_summary(results)
        self.assertIn("⚠️ 2 warnings", summary)
        self.assertNotIn("❌", summary)
    
    def test_format_summary_with_info_only(self):
        """
        Test formatting a summary with info items only.
        """
        results = {
            "issues": [
                {"severity": "info", "message": "Info 1"}
            ]
        }
        
        summary = self.formatter.format_summary(results)
        self.assertIn("✅ 1 info item", summary)
        self.assertNotIn("❌", summary)
        self.assertNotIn("⚠️", summary)


if __name__ == "__main__":
    unittest.main()

