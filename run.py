#!/usr/bin/env python
"""
Run script for the PR static analysis reporting system.
"""
import os
import sys
import json
import argparse
import logging
from datetime import datetime
from collections import namedtuple

from pr_static_analysis.reporting.reporting import ReportingSystem
from pr_static_analysis.reporting.delivery import (
    GitHubPRCommentDelivery,
    FileSystemDelivery,
    EmailDelivery
)
from pr_static_analysis.reporting.config import ReportingConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the PR static analysis reporting system.')
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to the configuration file')
    parser.add_argument('--results', type=str, default=None,
                        help='Path to the results file')
    parser.add_argument('--pr-number', type=int, default=123,
                        help='PR number')
    parser.add_argument('--pr-title', type=str, default='Example PR',
                        help='PR title')
    parser.add_argument('--pr-url', type=str, default='https://github.com/org/repo/pull/123',
                        help='PR URL')
    parser.add_argument('--pr-base', type=str, default='main',
                        help='PR base branch')
    parser.add_argument('--pr-head', type=str, default='feature-branch',
                        help='PR head branch')
    parser.add_argument('--format', type=str, default=None,
                        help='Output format (markdown, html, json)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory for file system delivery')
    parser.add_argument('--visualizations', action='store_true',
                        help='Include visualizations')
    parser.add_argument('--no-visualizations', action='store_false', dest='visualizations',
                        help='Do not include visualizations')
    parser.set_defaults(visualizations=None)
    
    return parser.parse_args()


def load_results(results_file):
    """Load results from a file."""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = []
    for item in data:
        results.append(AnalysisResult(
            rule_id=item['rule_id'],
            message=item['message'],
            severity=item['severity'],
            file=item.get('file'),
            line=item.get('line')
        ))
    
    return results


def create_sample_results():
    """Create sample results."""
    return [
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


def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    # Load configuration
    config = ReportingConfig(args.config)
    
    # Override configuration with command line arguments
    if args.format:
        config.set('default_format', args.format)
    
    if args.output_dir:
        config.set('delivery.file_system.output_dir', args.output_dir)
    
    if args.visualizations is not None:
        config.set('include_visualizations', args.visualizations)
    
    # Create PR context
    pr_context = PRContext(
        number=args.pr_number,
        title=args.pr_title,
        html_url=args.pr_url,
        base_ref=args.pr_base,
        head_ref=args.pr_head
    )
    
    # Load results
    if args.results:
        results = load_results(args.results)
    else:
        results = create_sample_results()
    
    # Create reporting system
    reporting_system = ReportingSystem()
    
    # Configure delivery channels
    if config.get('delivery.github_pr_comment.enabled', False):
        # This is a placeholder - in a real implementation, you would
        # create a GitHub client and pass it to the delivery channel
        github_client = None
        reporting_system.add_delivery_channel(
            GitHubPRCommentDelivery(github_client)
        )
        logger.info("Added GitHub PR comment delivery channel")
    
    if config.get('delivery.file_system.enabled', False):
        output_dir = config.get('delivery.file_system.output_dir', 'reports')
        reporting_system.add_delivery_channel(
            FileSystemDelivery(output_dir)
        )
        logger.info(f"Added file system delivery channel with output directory: {output_dir}")
    
    if config.get('delivery.email.enabled', False):
        smtp_config = config.get('delivery.email.smtp', {})
        recipients = config.get('delivery.email.recipients', [])
        
        if smtp_config and recipients:
            reporting_system.add_delivery_channel(
                EmailDelivery(smtp_config, recipients)
            )
            logger.info(f"Added email delivery channel with {len(recipients)} recipients")
    
    # Process results
    format_type = config.get('default_format', 'markdown')
    include_visualizations = config.get('include_visualizations', True)
    
    logger.info(f"Processing results with format: {format_type}, "
                f"include_visualizations: {include_visualizations}")
    
    result = reporting_system.process_results(
        results=results,
        pr_context=pr_context,
        format_type=format_type,
        include_visualizations=include_visualizations
    )
    
    # Print delivery results
    logger.info("Delivery results:")
    for channel, success in result['delivery_results'].items():
        logger.info(f"  {channel}: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    main()

