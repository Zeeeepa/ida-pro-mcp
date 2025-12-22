# PR Static Analysis Reporting System

This directory contains the reporting components for the PR static analysis system. The reporting system is responsible for generating, formatting, and delivering reports based on the results of PR static analysis.

## Components

### Report Generator

The `ReportGenerator` class in `report_generator.py` is responsible for collecting and organizing analysis results, and generating reports based on those results. It provides the following functionality:

- **Result Collection**:
  - `collect_results(context)`: Collect results from the analysis context
  - `filter_results_by_severity(severity)`: Filter results by severity
  - `filter_results_by_category(category)`: Filter results by category
  - `sort_results(key)`: Sort results by a specific key

- **Report Generation**:
  - `generate_summary_report()`: Generate a summary report
  - `generate_detailed_report()`: Generate a detailed report
  - `generate_issue_report()`: Generate a report focused on issues
  - `generate_custom_report(template)`: Generate a custom report using a template

- **Report Customization**:
  - `set_report_options(options)`: Set options for report generation
  - `add_custom_section(section)`: Add a custom section to the report
  - `set_report_metadata(metadata)`: Set metadata for the report

### Report Formatter

The formatters in `report_formatter.py` are responsible for formatting reports in different output formats:

- **HTMLFormatter**:
  - `format_report(report)`: Format a report as HTML
  - `format_result(result)`: Format a single result as HTML
  - `format_section(section)`: Format a section as HTML
  - `get_html_template()`: Get the HTML template for reports

- **MarkdownFormatter**:
  - `format_report(report)`: Format a report as Markdown
  - `format_result(result)`: Format a single result as Markdown
  - `format_section(section)`: Format a section as Markdown
  - `get_markdown_template()`: Get the Markdown template for reports

- **JSONFormatter**:
  - `format_report(report)`: Format a report as JSON
  - `format_result(result)`: Format a single result as JSON
  - `format_section(section)`: Format a section as JSON

### Visualization

The visualization functions in `visualization.py` are responsible for creating visualizations of analysis results:

- **Charts**:
  - `create_severity_chart(results)`: Create a chart showing results by severity
  - `create_category_chart(results)`: Create a chart showing results by category
  - `create_file_chart(results)`: Create a chart showing results by file

- **Graphs**:
  - `create_dependency_graph(results)`: Create a graph showing dependencies
  - `create_call_graph(results)`: Create a graph showing function calls
  - `create_inheritance_graph(results)`: Create a graph showing class inheritance

- **Code Highlighting**:
  - `highlight_code(code, language)`: Highlight code syntax
  - `highlight_diff(diff)`: Highlight diff syntax
  - `highlight_issues(code, issues)`: Highlight issues in code

### Delivery

The delivery functions in `delivery.py` are responsible for delivering reports to different destinations:

- **GitHub Delivery**:
  - `post_report_as_comment(repo, pr_number, report)`: Post a report as a PR comment
  - `post_report_as_review(repo, pr_number, report)`: Post a report as a PR review
  - `post_report_as_check(repo, commit_sha, report)`: Post a report as a check run

- **File Delivery**:
  - `save_report_to_file(report, file_path)`: Save a report to a file
  - `save_report_to_directory(report, directory)`: Save a report to a directory

- **Web Delivery**:
  - `serve_report(report, port)`: Serve a report via a web server
  - `create_report_url(report)`: Create a URL for a report

## Usage

Here's a simple example of how to use the reporting system:

```python
from pr_analysis.reporting import (
    ReportGenerator,
    HTMLFormatter,
    MarkdownFormatter,
    JSONFormatter,
    post_report_as_comment,
    save_report_to_file,
)

# Create a report generator
generator = ReportGenerator()

# Collect results from the analysis context
results = generator.collect_results(analysis_context)

# Filter results by severity
critical_errors = generator.filter_results_by_severity(["critical", "error"])

# Generate a report
report = generator.generate_detailed_report()

# Format the report as HTML
formatter = HTMLFormatter()
html_report = formatter.format_report(report)

# Save the report to a file
save_report_to_file(report, "report.html", "html")

# Post the report as a PR comment
post_report_as_comment("owner/repo", 123, report)
```

For more detailed examples, see the `test_reporting.py` script.

## Dependencies

The reporting system has the following dependencies:

- **Required**:
  - Python 3.6+
  - Standard library modules: json, html, re, base64, io, os, tempfile, http.server, socketserver, threading, webbrowser

- **Optional**:
  - matplotlib: For creating charts
  - networkx: For creating graphs
  - pygments: For code highlighting
  - PyGithub: For GitHub integration

## Testing

To test the reporting system, run the `test_reporting.py` script:

```bash
python -m pr_analysis.reporting.test_reporting
```

This will generate sample reports, format them in different formats, create visualizations, and demonstrate the delivery mechanisms.

