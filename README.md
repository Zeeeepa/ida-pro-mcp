# PR Static Analysis System

A static analysis system for pull requests that helps identify issues and enforce coding standards.

## Overview

This system analyzes pull requests to identify issues and enforce coding standards. It consists of several components:

1. **Core Analysis Engine**: Executes rules against the PR code
2. **Rule System**: Defines rules for static analysis
3. **GitHub Integration**: Integrates with GitHub to analyze PRs
4. **Reporting System**: Generates and delivers analysis reports

This repository contains the implementation of the Reporting System component.

## Reporting System

The reporting system is responsible for generating, formatting, and delivering analysis reports to different output channels. It includes the following components:

- **Report Generator**: Creates analysis reports from rule results
- **Report Formatters**: Format reports for different output formats (Markdown, HTML, JSON)
- **Visualization Components**: Visualize analysis results
- **Delivery Components**: Deliver reports to different output channels

For more information, see the [Reporting System README](pr_static_analysis/reporting/README.md).

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/pr-static-analysis.git
cd pr-static-analysis

# Install the package
pip install -e .
```

## Usage

```python
from pr_static_analysis.reporting.reporting import ReportingSystem
from pr_static_analysis.reporting.delivery import GitHubPRCommentDelivery

# Create a reporting system
reporting_system = ReportingSystem()

# Add a delivery channel
reporting_system.add_delivery_channel(GitHubPRCommentDelivery(github_client))

# Process analysis results
result = reporting_system.process_results(
    results=results,
    pr_context=pr_context,
    format_type="markdown",
    include_visualizations=True
)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8

# Run formatting
black .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

