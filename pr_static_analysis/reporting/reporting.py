"""
Main reporting module for PR static analysis.

This module provides the main entry point for the reporting system.
"""
from typing import List, Dict, Any, Optional
import logging

from .report_generator import ReportGenerator
from .report_formatter import ReportFormatterFactory
from .visualization import ReportVisualizer
from .delivery import ReportDeliveryService, ReportDeliveryChannel

logger = logging.getLogger(__name__)


class ReportingSystem:
    """Main reporting system for PR static analysis."""
    
    def __init__(self):
        """Initialize the reporting system."""
        self.report_generator = ReportGenerator()
        self.visualizer = ReportVisualizer()
        self.delivery_service = ReportDeliveryService()
    
    def add_delivery_channel(self, channel: ReportDeliveryChannel):
        """Add a delivery channel.
        
        Args:
            channel: The delivery channel to add
        """
        self.delivery_service.add_channel(channel)
    
    def process_results(self, results: list, pr_context: Any, 
                        format_type: str = 'markdown', 
                        include_visualizations: bool = True) -> Dict[str, Any]:
        """Process analysis results and generate a report.
        
        Args:
            results: List of analysis results
            pr_context: Context information about the PR
            format_type: Output format type (markdown, html, json)
            include_visualizations: Whether to include visualizations
            
        Returns:
            Dict containing the report and delivery results
        """
        # Generate report
        report = self.report_generator.generate_report(results, pr_context)
        
        # Add visualizations if requested and not JSON format
        if include_visualizations and format_type.lower() != 'json':
            report['visualizations'] = self._generate_visualizations(report)
        
        # Format report
        formatter = ReportFormatterFactory.create_formatter(format_type)
        formatted_report = formatter.format_report(report)
        
        # Deliver report
        delivery_results = self.delivery_service.deliver_report(report, formatted_report)
        
        return {
            'report': report,
            'formatted_report': formatted_report,
            'delivery_results': delivery_results
        }
    
    def _generate_visualizations(self, report: Dict[str, Any]) -> Dict[str, str]:
        """Generate visualizations for a report.
        
        Args:
            report: The report to visualize
            
        Returns:
            Dict mapping visualization names to base64 encoded PNG images
        """
        try:
            return {
                'summary_chart': self.visualizer.generate_summary_chart(report),
                'severity_distribution': self.visualizer.generate_severity_distribution(report),
                'file_heatmap': self.visualizer.generate_file_heatmap(report)
            }
        except Exception as e:
            logger.error(f"Failed to generate visualizations: {e}")
            return {}

