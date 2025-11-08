# PR Static Analysis Reporting System

This module provides a flexible reporting system for PR static analysis results. It supports different report formats, visualizations, and delivery channels.

## Features

- **Multiple Report Formats**: Generate reports in Markdown, HTML, JSON, and plain text formats.
- **Visualizations**: Create charts, graphs, and tables to visualize analysis results.
- **Delivery Channels**: Deliver reports through GitHub, email, Slack, or save them to files.
- **Customization**: Customize report templates, sections, and styling.
- **Extensibility**: Easily add new formatters, visualizations, and delivery channels.

## Architecture

The reporting system is built with a modular architecture:

- **ReportGenerator**: Main class that orchestrates the process of generating and delivering reports.
- **Formatters**: Convert analysis results into various formats (Markdown, HTML, JSON, text).
- **Visualizations**: Generate visual representations of analysis results (charts, graphs, tables).
- **Delivery Channels**: Send reports to various destinations (GitHub, email, Slack, files).
- **Utilities**: Helper functions for configuration, templates, etc.

## Usage

### Basic Usage

```python
from pr_static_analysis.reporting import ReportGenerator
from pr_static_analysis.reporting.formatters import MarkdownFormatter
from pr_static_analysis.reporting.delivery import FileDelivery

# Create a report generator
report_generator = ReportGenerator()

# Register formatters and delivery channels
report_generator.register_formatter('markdown', MarkdownFormatter())
report_generator.register_delivery_channel('file', FileDelivery())

# Generate and deliver a report
report = report_generator.generate_report(analysis_results, 'markdown')
report_generator.deliver_report(report, 'file', filename='pr_analysis.md')
```

### Adding Visualizations

```python
from pr_static_analysis.reporting.visualization import ChartVisualization

# Create and register a visualization
chart_viz = ChartVisualization(chart_type='bar', title='Metrics')
report_generator.register_visualization('metrics_chart', chart_viz)

# Generate a report with visualizations
report = report_generator.generate_report(
    analysis_results,
    'html',
    visualization_names=['metrics_chart']
)
```

### Customizing Reports

```python
# Create a formatter with custom sections
markdown_formatter = MarkdownFormatter(
    include_summary=True,
    include_details=True,
    include_issues=True,
    include_files=True,
    include_metrics=True,
    custom_sections={
        'Performance Impact': lambda results: results.get('performance_impact', 'No impact'),
        'Security Considerations': 'All security checks passed.'
    }
)

# Register the formatter
report_generator.register_formatter('markdown', markdown_formatter)
```

### Delivering to GitHub

```python
from pr_static_analysis.reporting.delivery import GitHubDelivery

# Create and register a GitHub delivery channel
github_delivery = GitHubDelivery(
    token='your-github-token',
    repo_name='owner/repo'
)
report_generator.register_delivery_channel('github', github_delivery)

# Deliver a report to a GitHub PR
report_generator.deliver_report(
    report,
    'github',
    pr_number=123
)
```

## Extending the System

### Creating a Custom Formatter

```python
from pr_static_analysis.reporting.formatters import BaseFormatter

class CustomFormatter(BaseFormatter):
    def format(self, analysis_results, visualizations=None, **kwargs):
        # Implement your custom formatting logic
        return formatted_report
```

### Creating a Custom Delivery Channel

```python
from pr_static_analysis.reporting.delivery import BaseDelivery

class CustomDelivery(BaseDelivery):
    def deliver(self, report, **kwargs):
        # Implement your custom delivery logic
        return success
```

### Creating a Custom Visualization

```python
from pr_static_analysis.reporting.visualization import BaseVisualization

class CustomVisualization(BaseVisualization):
    def generate(self, analysis_results, **kwargs):
        # Implement your custom visualization logic
        return visualization_data
```

## Dependencies

- **Required**:
  - Python 3.6+

- **Optional**:
  - Matplotlib (for chart visualizations)
  - Networkx (for graph visualizations)
  - PyGithub (for GitHub delivery)
  - Requests (for Slack delivery)
  - PyYAML (for YAML configuration files)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

