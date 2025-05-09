"""
Test script for the PR static analysis reporting system.

This script demonstrates the usage of the reporting system components.
"""

import os
import sys
from typing import List

from .report_generator import ReportGenerator, ReportResult, ReportSection, Report
from .report_formatter import HTMLFormatter, MarkdownFormatter, JSONFormatter
from .visualization import (
    create_severity_chart,
    create_category_chart,
    create_file_chart,
    highlight_code,
    highlight_diff,
    highlight_issues,
)
from .delivery import (
    save_report_to_file,
    save_report_to_directory,
    serve_report,
    create_report_url,
)


def create_sample_results() -> List[ReportResult]:
    """Create sample results for testing."""
    return [
        ReportResult(
            message="Missing return type annotation",
            severity="warning",
            category="type_checking",
            file_path="src/main.py",
            line_number=42,
            column=1,
            code_snippet="def process_data(data):\n    return data.process()",
            rule_id="missing-return-type",
        ),
        ReportResult(
            message="Unused import",
            severity="info",
            category="imports",
            file_path="src/utils.py",
            line_number=5,
            column=1,
            code_snippet="import os\nimport sys\nimport json  # Unused import",
            rule_id="unused-import",
        ),
        ReportResult(
            message="Potential division by zero",
            severity="error",
            category="logic",
            file_path="src/calculator.py",
            line_number=78,
            column=10,
            code_snippet="result = numerator / denominator  # denominator could be zero",
            rule_id="division-by-zero",
        ),
        ReportResult(
            message="SQL injection vulnerability",
            severity="critical",
            category="security",
            file_path="src/database.py",
            line_number=123,
            column=12,
            code_snippet="query = f\"SELECT * FROM users WHERE username = '{username}'\"",
            rule_id="sql-injection",
        ),
    ]


def test_report_generator():
    """Test the ReportGenerator class."""
    print("Testing ReportGenerator...")
    
    # Create a report generator
    generator = ReportGenerator()
    
    # Add sample results
    results = create_sample_results()
    generator.results = results
    
    # Set report metadata
    generator.set_report_metadata({
        "repository": "example/repo",
        "pr_number": 123,
        "commit_sha": "abc123",
        "analysis_date": "2023-01-01",
    })
    
    # Add custom sections
    generator.add_custom_section(ReportSection(
        title="Code Quality Summary",
        content="The code quality is generally good, but there are some issues that should be addressed.",
        order=1,
    ))
    
    # Generate reports
    summary_report = generator.generate_summary_report()
    detailed_report = generator.generate_detailed_report()
    issue_report = generator.generate_issue_report()
    
    print("  Summary report generated")
    print("  Detailed report generated")
    print("  Issue report generated")
    
    return summary_report, detailed_report, issue_report


def test_report_formatters(report: Report):
    """Test the report formatters."""
    print("Testing report formatters...")
    
    # Format as HTML
    html_formatter = HTMLFormatter()
    html_report = html_formatter.format_report(report)
    print("  HTML formatter: OK")
    
    # Format as Markdown
    md_formatter = MarkdownFormatter()
    md_report = md_formatter.format_report(report)
    print("  Markdown formatter: OK")
    
    # Format as JSON
    json_formatter = JSONFormatter()
    json_report = json_formatter.format_report(report)
    print("  JSON formatter: OK")
    
    return html_report, md_report, json_report


def test_visualizations(results: List[ReportResult]):
    """Test the visualization functions."""
    print("Testing visualizations...")
    
    # Create charts
    severity_chart = create_severity_chart(results)
    print("  Severity chart: OK")
    
    category_chart = create_category_chart(results)
    print("  Category chart: OK")
    
    file_chart = create_file_chart(results)
    print("  File chart: OK")
    
    # Test code highlighting
    code = "def hello_world():\n    print('Hello, world!')\n"
    highlighted_code = highlight_code(code, "python")
    print("  Code highlighting: OK")
    
    # Test diff highlighting
    diff = "@@ -1,3 +1,3 @@\n def hello_world():\n-    print('Hello, world!')\n+    print('Hello, universe!')\n"
    highlighted_diff = highlight_diff(diff)
    print("  Diff highlighting: OK")
    
    # Test issue highlighting
    issues = [
        {"line": 2, "column": 5, "message": "Use double quotes", "severity": "info"},
    ]
    highlighted_issues = highlight_issues(code, issues)
    print("  Issue highlighting: OK")


def test_delivery(report: Report):
    """Test the delivery mechanisms."""
    print("Testing delivery mechanisms...")
    
    # Save to file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "report.html")
    save_report_to_file(report, html_path, "html")
    print(f"  Saved HTML report to {html_path}")
    
    md_path = os.path.join(output_dir, "report.md")
    save_report_to_file(report, md_path, "markdown")
    print(f"  Saved Markdown report to {md_path}")
    
    json_path = os.path.join(output_dir, "report.json")
    save_report_to_file(report, json_path, "json")
    print(f"  Saved JSON report to {json_path}")
    
    # Save to directory
    dir_path = os.path.join(output_dir, "reports")
    file_paths = save_report_to_directory(report, dir_path)
    print(f"  Saved reports to directory {dir_path}")
    
    # Create URL
    url = create_report_url(report)
    print(f"  Created report URL: {url}")
    
    # Serve report (commented out to avoid blocking the test)
    # serve_url = serve_report(report, 8000)
    # print(f"  Serving report at {serve_url}")


def main():
    """Run the test script."""
    print("PR Static Analysis Reporting System Test")
    print("=======================================")
    
    # Test report generator
    summary_report, detailed_report, issue_report = test_report_generator()
    
    # Test report formatters
    html_report, md_report, json_report = test_report_formatters(detailed_report)
    
    # Test visualizations
    test_visualizations(create_sample_results())
    
    # Test delivery
    test_delivery(detailed_report)
    
    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    main()

