#!/usr/bin/env python3
"""
Example script demonstrating the PR static analysis reporting system.
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pr_static_analysis.reporting import ReportGenerator
from src.pr_static_analysis.reporting.formatters import (
    MarkdownFormatter,
    HTMLFormatter,
    JSONFormatter,
    TextFormatter
)
from src.pr_static_analysis.reporting.delivery import (
    FileDelivery,
    GitHubDelivery,
    EmailDelivery,
    SlackDelivery
)
from src.pr_static_analysis.reporting.visualization import (
    ChartVisualization,
    GraphVisualization,
    TableVisualization
)


def main():
    """Main function."""
    # Create a sample analysis result
    analysis_results = {
        'summary': 'This is a sample PR static analysis report.',
        'issues': [
            {
                'severity': 'error',
                'message': 'Missing error handling',
                'file': 'src/main.py',
                'line': 42
            },
            {
                'severity': 'warning',
                'message': 'Unused variable',
                'file': 'src/utils.py',
                'line': 15
            },
            {
                'severity': 'info',
                'message': 'Consider adding a docstring',
                'file': 'src/models.py',
                'line': 23
            }
        ],
        'files_added': [
            'src/new_feature.py',
            'tests/test_new_feature.py'
        ],
        'files_modified': [
            'src/main.py',
            'src/utils.py',
            'src/models.py'
        ],
        'files_removed': [
            'src/deprecated.py'
        ],
        'metrics': {
            'complexity_change': 5,
            'function_count_change': 3,
            'class_count_change': 1,
            'lines_added': 120,
            'lines_removed': 45
        },
        'details': {
            'Performance Impact': 'Minimal impact on performance.',
            'Security Considerations': 'No security issues identified.',
            'Test Coverage': 'Test coverage increased by 2%.'
        }
    }
    
    # Create a report generator
    report_generator = ReportGenerator()
    
    # Register formatters
    report_generator.register_formatter('markdown', MarkdownFormatter())
    report_generator.register_formatter('html', HTMLFormatter(use_bootstrap=True))
    report_generator.register_formatter('json', JSONFormatter(pretty_print=True))
    report_generator.register_formatter('text', TextFormatter())
    
    # Register delivery channels
    report_generator.register_delivery_channel('file', FileDelivery(default_output_dir='reports'))
    
    # Register visualizations
    try:
        chart_viz = ChartVisualization(chart_type='bar', title='Metrics')
        report_generator.register_visualization('metrics_chart', chart_viz)
    except ImportError:
        print("Matplotlib not installed, skipping chart visualization")
    
    try:
        graph_viz = GraphVisualization(graph_type='directed', title='File Dependencies')
        report_generator.register_visualization('file_dependencies', graph_viz)
    except ImportError:
        print("Networkx not installed, skipping graph visualization")
    
    table_viz = TableVisualization(format='html', caption='Issues Summary')
    report_generator.register_visualization('issues_table', table_viz)
    
    # Generate reports in different formats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate and deliver Markdown report
    markdown_report = report_generator.generate_report(
        analysis_results,
        'markdown',
        visualization_names=['issues_table'],
        title='PR Static Analysis Report (Markdown)'
    )
    report_generator.deliver_report(
        markdown_report,
        'file',
        filename=f'pr_analysis_{timestamp}',
        extension='md'
    )
    
    # Generate and deliver HTML report
    html_report = report_generator.generate_report(
        analysis_results,
        'html',
        visualization_names=['metrics_chart', 'file_dependencies', 'issues_table'],
        title='PR Static Analysis Report (HTML)'
    )
    report_generator.deliver_report(
        html_report,
        'file',
        filename=f'pr_analysis_{timestamp}',
        extension='html'
    )
    
    # Generate and deliver JSON report
    json_report = report_generator.generate_report(
        analysis_results,
        'json',
        title='PR Static Analysis Report (JSON)'
    )
    report_generator.deliver_report(
        json_report,
        'file',
        filename=f'pr_analysis_{timestamp}',
        extension='json'
    )
    
    # Generate and deliver Text report
    text_report = report_generator.generate_report(
        analysis_results,
        'text',
        title='PR Static Analysis Report (Text)'
    )
    report_generator.deliver_report(
        text_report,
        'file',
        filename=f'pr_analysis_{timestamp}',
        extension='txt'
    )
    
    print(f"Reports generated and saved to the 'reports' directory with timestamp {timestamp}")


if __name__ == '__main__':
    main()

