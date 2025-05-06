#!/usr/bin/env python3
"""
Example script demonstrating the PR static analysis reporting system.

This script shows how to use the reporting system to generate and deliver reports
in various formats using different delivery channels.
"""

import os
import sys
import logging
from typing import Dict, List, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pr_static_analysis.reporting.report_generator import ReportGenerator
from src.pr_static_analysis.reporting.formatters.markdown_formatter import MarkdownFormatter
from src.pr_static_analysis.reporting.formatters.html_formatter import HTMLFormatter
from src.pr_static_analysis.reporting.formatters.json_formatter import JSONFormatter
from src.pr_static_analysis.reporting.formatters.text_formatter import TextFormatter
from src.pr_static_analysis.reporting.delivery.file_delivery import FileDelivery
from src.pr_static_analysis.reporting.delivery.github_delivery import GitHubDelivery
from src.pr_static_analysis.reporting.delivery.slack_delivery import SlackDelivery
from src.pr_static_analysis.reporting.delivery.email_delivery import EmailDelivery
from src.pr_static_analysis.reporting.visualization.chart_visualization import SeverityPieChart, CategoryBarChart
from src.pr_static_analysis.reporting.visualization.graph_visualization import FileHeatmap
from src.pr_static_analysis.reporting.visualization.table_visualization import ResultsTable
from src.pr_static_analysis.reporting.utils.template import ReportTemplate, ReportSection
from src.pr_static_analysis.reporting.utils.config import ReportConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_results() -> List[Dict[str, Any]]:
    """Generate sample analysis results for demonstration."""
    return [
        {
            "rule_id": "security-001",
            "message": "Potential SQL injection vulnerability",
            "file_path": "src/app/database.py",
            "line": 42,
            "severity": "critical",
            "category": "security"
        },
        {
            "rule_id": "style-101",
            "message": "Line exceeds maximum length (120 characters)",
            "file_path": "src/app/views.py",
            "line": 78,
            "severity": "info",
            "category": "style"
        },
        {
            "rule_id": "performance-052",
            "message": "Inefficient database query detected",
            "file_path": "src/app/models.py",
            "line": 156,
            "severity": "warning",
            "category": "performance"
        },
        {
            "rule_id": "security-042",
            "message": "Hardcoded credentials detected",
            "file_path": "src/app/config.py",
            "line": 23,
            "severity": "critical",
            "category": "security"
        },
        {
            "rule_id": "bug-127",
            "message": "Potential null pointer dereference",
            "file_path": "src/app/utils.py",
            "line": 89,
            "severity": "error",
            "category": "bug"
        }
    ]

def generate_sample_metadata() -> Dict[str, Any]:
    """Generate sample metadata for demonstration."""
    return {
        "repository": "example/repo",
        "pull_request": 123,
        "commit_sha": "abc123def456",
        "analysis_date": "2025-05-06T10:00:00Z",
        "analyzer_version": "1.0.0"
    }

def main():
    """Run the reporting system example."""
    logger.info("Starting PR static analysis reporting example")
    
    # Create the report generator
    report_generator = ReportGenerator()
    
    # Register formatters
    report_generator.register_formatter("markdown", MarkdownFormatter())
    report_generator.register_formatter("html", HTMLFormatter())
    report_generator.register_formatter("json", JSONFormatter())
    report_generator.register_formatter("text", TextFormatter())
    
    # Add sample results and metadata
    results = generate_sample_results()
    metadata = generate_sample_metadata()
    report_generator.add_results(results)
    report_generator.set_metadata(metadata)
    
    # Generate reports in different formats
    markdown_report = report_generator.generate_report("markdown")
    html_report = report_generator.generate_report("html")
    json_report = report_generator.generate_report("json")
    text_report = report_generator.generate_report("text")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Deliver reports using file delivery
    file_delivery = FileDelivery()
    file_delivery.deliver(markdown_report, file_path=os.path.join(output_dir, "report.md"))
    file_delivery.deliver(html_report, file_path=os.path.join(output_dir, "report.html"))
    file_delivery.deliver(json_report, file_path=os.path.join(output_dir, "report.json"))
    file_delivery.deliver(text_report, file_path=os.path.join(output_dir, "report.txt"))
    
    logger.info("Reports delivered to files in the output directory")
    
    # Example of using visualizations
    severity_chart = SeverityPieChart()
    severity_chart_img = severity_chart.generate(results)
    
    category_chart = CategoryBarChart()
    category_chart_img = category_chart.generate(results)
    
    file_heatmap = FileHeatmap()
    file_heatmap_img = file_heatmap.generate(results)
    
    results_table = ResultsTable()
    results_table_html = results_table.generate(results)
    
    # Example of using templates and sections
    template_str = """
# PR Analysis Report for {{ repository }}

## Summary
{{ summary }}

## Visualizations
{{ visualizations }}

## Detailed Results
{{ results }}
"""
    
    template = ReportTemplate(template_str)
    
    # Create sections
    summary_section = ReportSection("Summary", "Found {{ total_issues }} issues ({{ critical_count }} critical, {{ error_count }} errors, {{ warning_count }} warnings)")
    visualizations_section = ReportSection("Visualizations", "Severity distribution: ![Severity Chart]({{ severity_chart }})")
    results_section = ReportSection("Results", results_table_html)
    
    # Create context for template rendering
    context = {
        "repository": metadata["repository"],
        "total_issues": len(results),
        "critical_count": len([r for r in results if r.get("severity") == "critical"]),
        "error_count": len([r for r in results if r.get("severity") == "error"]),
        "warning_count": len([r for r in results if r.get("severity") == "warning"]),
        "severity_chart": severity_chart_img,
        "category_chart": category_chart_img,
        "file_heatmap": file_heatmap_img,
        "results_table": results_table_html
    }
    
    # Render the template
    custom_report = template.render(context)
    
    # Save the custom report
    file_delivery.deliver(custom_report, file_path=os.path.join(output_dir, "custom_report.md"))
    
    logger.info("Custom report generated and delivered")
    
    # Example of using report configuration
    config = ReportConfig()
    config.set("include_summary", True)
    config.set("include_visualizations", True)
    config.set("severity_filter", ["critical", "error"])
    config.set("max_results", 10)
    
    # Apply configuration to report generator
    report_generator.apply_config(config)
    
    # Generate a configured report
    configured_report = report_generator.generate_report("markdown")
    file_delivery.deliver(configured_report, file_path=os.path.join(output_dir, "configured_report.md"))
    
    logger.info("Configured report generated and delivered")
    
    # Example of GitHub delivery (commented out as it requires GitHub credentials)
    """
    github_delivery = GitHubDelivery(github_token="your_github_token")
    github_delivery.deliver(markdown_report, repo_name="example/repo", pr_number=123)
    """
    
    # Example of Slack delivery (commented out as it requires Slack webhook URL)
    """
    slack_delivery = SlackDelivery(webhook_url="your_slack_webhook_url")
    slack_delivery.deliver(text_report, channel="#pr-analysis", username="PR Analyzer")
    """
    
    # Example of Email delivery (commented out as it requires email credentials)
    """
    email_delivery = EmailDelivery(
        smtp_server="smtp.example.com",
        smtp_port=587,
        username="your_email@example.com",
        password="your_password"
    )
    email_delivery.deliver(
        html_report,
        from_addr="your_email@example.com",
        to_addr="recipient@example.com",
        subject="PR Analysis Report",
        is_html=True
    )
    """
    
    logger.info("PR static analysis reporting example completed")

if __name__ == "__main__":
    main()

