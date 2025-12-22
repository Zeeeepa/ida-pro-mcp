"""
Reporting components for the PR static analysis system.

This package contains components for generating, formatting, and delivering reports
based on the results of PR static analysis.
"""

from .report_generator import ReportGenerator
from .report_formatter import HTMLFormatter, MarkdownFormatter, JSONFormatter
from .visualization import (
    create_severity_chart,
    create_category_chart,
    create_file_chart,
    create_dependency_graph,
    create_call_graph,
    create_inheritance_graph,
    highlight_code,
    highlight_diff,
    highlight_issues,
)
from .delivery import (
    post_report_as_comment,
    post_report_as_review,
    post_report_as_check,
    save_report_to_file,
    save_report_to_directory,
    serve_report,
    create_report_url,
)

__all__ = [
    "ReportGenerator",
    "HTMLFormatter",
    "MarkdownFormatter",
    "JSONFormatter",
    "create_severity_chart",
    "create_category_chart",
    "create_file_chart",
    "create_dependency_graph",
    "create_call_graph",
    "create_inheritance_graph",
    "highlight_code",
    "highlight_diff",
    "highlight_issues",
    "post_report_as_comment",
    "post_report_as_review",
    "post_report_as_check",
    "save_report_to_file",
    "save_report_to_directory",
    "serve_report",
    "create_report_url",
]
