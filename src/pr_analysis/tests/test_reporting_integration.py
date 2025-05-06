"""
Integration test for the PR static analysis reporting system.

This script demonstrates how the reporting system integrates with the rest of the
PR static analysis system.
"""

import os
import sys
import json
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import reporting components
from reporting import (
    ReportGenerator,
    HTMLFormatter,
    MarkdownFormatter,
    JSONFormatter,
    save_report_to_file,
    save_report_to_directory,
)

# Mock analysis context and results for testing
class MockAnalysisContext:
    """Mock analysis context for testing."""
    
    def __init__(self, results: List[Dict[str, Any]]):
        """Initialize the mock context with results."""
        self.results = results
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get the analysis results."""
        return self.results


def create_mock_context() -> MockAnalysisContext:
    """Create a mock analysis context with sample results."""
    results = [
        {
            "message": "Missing return type annotation",
            "severity": "warning",
            "category": "type_checking",
            "file_path": "src/main.py",
            "line_number": 42,
            "column": 1,
            "code_snippet": "def process_data(data):\n    return data.process()",
            "rule_id": "missing-return-type",
        },
        {
            "message": "Unused import",
            "severity": "info",
            "category": "imports",
            "file_path": "src/utils.py",
            "line_number": 5,
            "column": 1,
            "code_snippet": "import os\nimport sys\nimport json  # Unused import",
            "rule_id": "unused-import",
        },
        {
            "message": "Potential division by zero",
            "severity": "error",
            "category": "logic",
            "file_path": "src/calculator.py",
            "line_number": 78,
            "column": 10,
            "code_snippet": "result = numerator / denominator  # denominator could be zero",
            "rule_id": "division-by-zero",
        },
        {
            "message": "SQL injection vulnerability",
            "severity": "critical",
            "category": "security",
            "file_path": "src/database.py",
            "line_number": 123,
            "column": 12,
            "code_snippet": "query = f\"SELECT * FROM users WHERE username = '{username}'\"",
            "rule_id": "sql-injection",
        },
    ]
    
    return MockAnalysisContext(results)


def test_integration():
    """Test the integration of the reporting system with the analysis context."""
    print("PR Static Analysis Reporting Integration Test")
    print("============================================")
    
    # Create a mock analysis context
    context = create_mock_context()
    print("Created mock analysis context")
    
    # Create a report generator
    generator = ReportGenerator()
    print("Created report generator")
    
    # Collect results from the context
    results = generator.collect_results(context)
    print(f"Collected {len(results)} results from the context")
    
    # Set report metadata
    generator.set_report_metadata({
        "repository": "example/repo",
        "pr_number": 123,
        "commit_sha": "abc123",
        "analysis_date": "2023-01-01",
    })
    print("Set report metadata")
    
    # Generate a detailed report
    report = generator.generate_detailed_report()
    print("Generated detailed report")
    
    # Format the report as HTML
    formatter = HTMLFormatter()
    html_report = formatter.format_report(report)
    print("Formatted report as HTML")
    
    # Save the report to a file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "integration_report.html")
    save_report_to_file(report, html_path, "html")
    print(f"Saved HTML report to {html_path}")
    
    # Save the report in multiple formats
    dir_path = os.path.join(output_dir, "integration_reports")
    file_paths = save_report_to_directory(report, dir_path)
    print(f"Saved reports to directory {dir_path}")
    
    print("\nIntegration test completed successfully!")


if __name__ == "__main__":
    test_integration()

