"""
JSON Formatter Module

This module provides a formatter for converting analysis results into JSON format.
"""

import json
from typing import Any, Dict, Optional, List

from .base_formatter import BaseFormatter


class JSONFormatter(BaseFormatter):
    """
    Formatter for converting analysis results into JSON format.
    
    This formatter generates a JSON report from analysis results.
    It supports customization of the included fields and formatting options.
    """
    
    def __init__(
        self,
        include_summary: bool = True,
        include_details: bool = True,
        include_issues: bool = True,
        include_files: bool = True,
        include_metrics: bool = True,
        pretty_print: bool = True,
        custom_fields: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new JSONFormatter.
        
        Args:
            include_summary: Whether to include a summary field
            include_details: Whether to include a details field
            include_issues: Whether to include an issues field
            include_files: Whether to include files fields
            include_metrics: Whether to include a metrics field
            pretty_print: Whether to pretty-print the JSON output
            custom_fields: Optional dictionary of custom fields to include
        """
        self.include_summary = include_summary
        self.include_details = include_details
        self.include_issues = include_issues
        self.include_files = include_files
        self.include_metrics = include_metrics
        self.pretty_print = pretty_print
        self.custom_fields = custom_fields or {}
        
    def format(
        self, 
        analysis_results: Dict[str, Any], 
        visualizations: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Format analysis results into a JSON report.
        
        Args:
            analysis_results: Analysis results to format
            visualizations: Optional dictionary of visualization data
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            The formatted report as a JSON string
        """
        # Create a new dictionary for the report
        report = {}
        
        # Add title
        title = kwargs.get('title', 'PR Static Analysis Report')
        report['title'] = title
        
        # Add timestamp if provided
        if 'timestamp' in kwargs:
            report['timestamp'] = kwargs['timestamp']
        
        # Add summary
        if self.include_summary and 'summary' in analysis_results:
            report['summary'] = analysis_results['summary']
        
        # Add issues
        if self.include_issues and 'issues' in analysis_results:
            report['issues'] = analysis_results['issues']
        
        # Add files
        if self.include_files:
            if 'files_added' in analysis_results:
                report['files_added'] = analysis_results['files_added']
            if 'files_modified' in analysis_results:
                report['files_modified'] = analysis_results['files_modified']
            if 'files_removed' in analysis_results:
                report['files_removed'] = analysis_results['files_removed']
        
        # Add metrics
        if self.include_metrics and 'metrics' in analysis_results:
            report['metrics'] = analysis_results['metrics']
        
        # Add visualizations
        if visualizations:
            # For JSON, we can only include serializable data
            serializable_visualizations = {}
            for viz_name, viz_data in visualizations.items():
                if isinstance(viz_data, (str, int, float, bool, list, dict, type(None))):
                    serializable_visualizations[viz_name] = viz_data
                elif hasattr(viz_data, 'to_dict'):
                    # If the visualization object has a to_dict method, use it
                    serializable_visualizations[viz_name] = viz_data.to_dict()
                elif hasattr(viz_data, '__dict__'):
                    # If the visualization object has a __dict__ attribute, use it
                    serializable_visualizations[viz_name] = viz_data.__dict__
            
            if serializable_visualizations:
                report['visualizations'] = serializable_visualizations
        
        # Add custom fields
        for field_name, field_value in self.custom_fields.items():
            if callable(field_value):
                # If the field value is a function, call it with the analysis results
                report[field_name] = field_value(analysis_results)
            else:
                # Otherwise, add the value directly
                report[field_name] = field_value
        
        # Add details
        if self.include_details and 'details' in analysis_results:
            report['details'] = analysis_results['details']
        
        # Convert to JSON
        if self.pretty_print:
            return json.dumps(report, indent=2, sort_keys=True)
        else:
            return json.dumps(report)

