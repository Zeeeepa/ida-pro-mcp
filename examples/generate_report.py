"""
Example script for generating a report.
"""
import os
import sys
import json
from datetime import datetime
from collections import namedtuple

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pr_static_analysis.reporting.reporting import ReportingSystem
from pr_static_analysis.reporting.delivery import FileSystemDelivery


# Create a simple PR context
class PRContext:
    """Simple PR context for the example."""
    
    def __init__(self, number, title, html_url, base_ref, head_ref):
        """Initialize the PR context."""
        self.number = number
        self.title = title
        self.html_url = html_url
        self.base = namedtuple('Ref', ['ref'])(base_ref)
        self.head = namedtuple('Ref', ['ref'])(head_ref)


# Create a simple analysis result
class AnalysisResult:
    """Simple analysis result for the example."""
    
    def __init__(self, rule_id, message, severity, file=None, line=None):
        """Initialize the analysis result."""
        self.rule_id = rule_id
        self.message = message
        self.severity = severity
        self.file = file
        self.line = line
    
    def to_dict(self):
        """Convert the result to a dictionary."""
        return {
            'rule_id': self.rule_id,
            'message': self.message,
            'severity': self.severity,
            'file': self.file,
            'line': self.line
        }


def main():
    """Main function."""
    # Create a PR context
    pr_context = PRContext(
        number=123,
        title="Example PR",
        html_url="https://github.com/org/repo/pull/123",
        base_ref="main",
        head_ref="feature-branch"
    )
    
    # Create some analysis results
    results = [
        AnalysisResult(
            rule_id="E001",
            message="Missing docstring",
            severity="error",
            file="example.py",
            line=10
        ),
        AnalysisResult(
            rule_id="E002",
            message="Line too long",
            severity="error",
            file="example.py",
            line=20
        ),
        AnalysisResult(
            rule_id="W001",
            message="Unused variable",
            severity="warning",
            file="utils.py",
            line=30
        ),
        AnalysisResult(
            rule_id="I001",
            message="Consider using a list comprehension",
            severity="info",
            file="utils.py",
            line=40
        )
    ]
    
    # Create a reporting system
    reporting_system = ReportingSystem()
    
    # Add a file system delivery channel
    output_dir = os.path.join(os.path.dirname(__file__), 'reports')
    reporting_system.add_delivery_channel(FileSystemDelivery(output_dir))
    
    # Process the results
    result = reporting_system.process_results(
        results=results,
        pr_context=pr_context,
        format_type="markdown",
        include_visualizations=True
    )
    
    # Print the report
    print("Report generated successfully!")
    print(f"Report saved to: {output_dir}")
    
    # Print the delivery results
    print("\nDelivery results:")
    for channel, success in result['delivery_results'].items():
        print(f"  {channel}: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    main()

