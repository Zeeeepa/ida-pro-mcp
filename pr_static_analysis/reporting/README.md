# PR Static Analysis Reporting System

This module provides a reporting system for the PR static analysis system. It is responsible for generating, formatting, and delivering analysis reports to different output channels.

## Components

### Report Generator

The report generator creates analysis reports from rule results. It is implemented in `report_generator.py`.

```python
from pr_static_analysis.reporting.report_generator import ReportGenerator

# Create a report generator
generator = ReportGenerator()

# Generate a report
report = generator.generate_report(results, pr_context)
```

### Report Formatters

The report formatters format reports for different output formats (Markdown, HTML, JSON). They are implemented in `report_formatter.py`.

```python
from pr_static_analysis.reporting.report_formatter import ReportFormatterFactory

# Create a formatter
formatter = ReportFormatterFactory.create_formatter("markdown")

# Format a report
formatted_report = formatter.format_report(report)
```

### Visualization Components

The visualization components visualize analysis results. They are implemented in `visualization.py`.

```python
from pr_static_analysis.reporting.visualization import ReportVisualizer

# Create a visualizer
visualizer = ReportVisualizer()

# Generate a summary chart
chart = visualizer.generate_summary_chart(report)
```

### Delivery Components

The delivery components deliver reports to different output channels. They are implemented in `delivery.py`.

```python
from pr_static_analysis.reporting.delivery import GitHubPRCommentDelivery, ReportDeliveryService

# Create a delivery service
delivery_service = ReportDeliveryService()

# Add a delivery channel
delivery_service.add_channel(GitHubPRCommentDelivery(github_client))

# Deliver a report
results = delivery_service.deliver_report(report, formatted_report)
```

### Templates

The templates module provides customizable templates for reports. It is implemented in `templates.py`.

```python
from pr_static_analysis.reporting.templates import TemplateManager

# Create a template manager
template_manager = TemplateManager()

# Render a report
rendered_report = template_manager.render_report(report, "markdown")
```

### Configuration

The configuration module provides configuration functionality for the reporting system. It is implemented in `config.py`.

```python
from pr_static_analysis.reporting.config import ReportingConfig

# Create a configuration
config = ReportingConfig("config.json")

# Get a configuration value
value = config.get("default_format")
```

### Integration

The integration module provides integration with the core analysis engine. It is implemented in `integration.py`.

```python
from pr_static_analysis.reporting.integration import create_integration

# Create an integration
integration = create_integration("config.json")

# Process analysis results
result = integration.process_analysis_results(results, pr_context)
```

### Utilities

The utilities module provides utility functions for the reporting system. It is implemented in `utils.py`.

```python
from pr_static_analysis.reporting.utils import format_timestamp

# Format a timestamp
formatted = format_timestamp("2023-01-01T12:00:00")
```

## Usage

Here's a simple example of how to use the reporting system:

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

# Access the report and delivery results
report = result["report"]
formatted_report = result["formatted_report"]
delivery_results = result["delivery_results"]
```

## Testing

The reporting system includes unit tests for each component. You can run the tests using the following command:

```bash
python -m unittest discover -s pr_static_analysis/reporting/tests
```

