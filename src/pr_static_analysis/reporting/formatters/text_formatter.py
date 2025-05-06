"""
Text Formatter Module

This module provides a formatter for converting analysis results into plain text format.
"""

from typing import Any, Dict, Optional, List

from .base_formatter import BaseFormatter


class TextFormatter(BaseFormatter):
    """
    Formatter for converting analysis results into plain text format.
    
    This formatter generates a plain text report from analysis results.
    It supports customization of the report structure and content.
    """
    
    def __init__(
        self,
        include_summary: bool = True,
        include_details: bool = True,
        include_issues: bool = True,
        include_files: bool = True,
        include_metrics: bool = True,
        custom_sections: Optional[Dict[str, Any]] = None,
        line_width: int = 80
    ):
        """
        Initialize a new TextFormatter.
        
        Args:
            include_summary: Whether to include a summary section
            include_details: Whether to include a details section
            include_issues: Whether to include an issues section
            include_files: Whether to include a files section
            include_metrics: Whether to include a metrics section
            custom_sections: Optional dictionary of custom sections to include
            line_width: Maximum line width for the text output
        """
        self.include_summary = include_summary
        self.include_details = include_details
        self.include_issues = include_issues
        self.include_files = include_files
        self.include_metrics = include_metrics
        self.custom_sections = custom_sections or {}
        self.line_width = line_width
        
    def format(
        self, 
        analysis_results: Dict[str, Any], 
        visualizations: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Format analysis results into a plain text report.
        
        Args:
            analysis_results: Analysis results to format
            visualizations: Optional dictionary of visualization data
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            The formatted report as a plain text string
        """
        report_parts = []
        
        # Add title
        title = kwargs.get('title', 'PR Static Analysis Report')
        report_parts.append(title)
        report_parts.append('=' * min(len(title), self.line_width))
        report_parts.append("")
        
        # Add summary section
        if self.include_summary and 'summary' in analysis_results:
            report_parts.append("SUMMARY")
            report_parts.append('-' * 7)
            report_parts.append("")
            report_parts.append(analysis_results['summary'])
            report_parts.append("")
        
        # Add issues section
        if self.include_issues and 'issues' in analysis_results:
            report_parts.append("ISSUES")
            report_parts.append('-' * 6)
            report_parts.append("")
            
            issues = analysis_results['issues']
            if not issues:
                report_parts.append("No issues found.")
            else:
                for issue in issues:
                    severity = issue.get('severity', 'info').upper()
                    message = issue.get('message', '')
                    file = issue.get('file', '')
                    line = issue.get('line', '')
                    
                    location = ""
                    if file:
                        location = f" in {file}"
                        if line:
                            location += f" at line {line}"
                    
                    report_parts.append(f"[{severity}]{location}: {message}")
            
            report_parts.append("")
        
        # Add files section
        if self.include_files and any(k in analysis_results for k in ['files_added', 'files_modified', 'files_removed']):
            report_parts.append("FILES")
            report_parts.append('-' * 5)
            report_parts.append("")
            
            files_added = analysis_results.get('files_added', [])
            files_modified = analysis_results.get('files_modified', [])
            files_removed = analysis_results.get('files_removed', [])
            
            if files_added:
                report_parts.append("Files Added:")
                for file in sorted(files_added):
                    report_parts.append(f"  {file}")
                report_parts.append("")
            
            if files_modified:
                report_parts.append("Files Modified:")
                for file in sorted(files_modified):
                    report_parts.append(f"  {file}")
                report_parts.append("")
            
            if files_removed:
                report_parts.append("Files Removed:")
                for file in sorted(files_removed):
                    report_parts.append(f"  {file}")
                report_parts.append("")
        
        # Add metrics section
        if self.include_metrics and 'metrics' in analysis_results:
            report_parts.append("METRICS")
            report_parts.append('-' * 7)
            report_parts.append("")
            
            metrics = analysis_results['metrics']
            for key, value in metrics.items():
                # Format the key for better readability
                formatted_key = key.replace('_', ' ').title()
                report_parts.append(f"{formatted_key}: {value}")
            
            report_parts.append("")
        
        # Add visualizations (limited support in plain text)
        if visualizations:
            report_parts.append("VISUALIZATIONS")
            report_parts.append('-' * 14)
            report_parts.append("")
            
            for viz_name, viz_data in visualizations.items():
                formatted_name = viz_name.replace('_', ' ').title()
                report_parts.append(f"{formatted_name}:")
                
                if isinstance(viz_data, str):
                    # If the visualization is a string, add it directly
                    report_parts.append(viz_data)
                elif isinstance(viz_data, dict) and 'text' in viz_data:
                    # If the visualization has a 'text' key, use that
                    report_parts.append(viz_data['text'])
                else:
                    # Otherwise, convert to string
                    report_parts.append(str(viz_data))
                
                report_parts.append("")
        
        # Add custom sections
        for section_name, section_content in self.custom_sections.items():
            report_parts.append(section_name.upper())
            report_parts.append('-' * len(section_name))
            report_parts.append("")
            
            if callable(section_content):
                # If the section content is a function, call it with the analysis results
                content = section_content(analysis_results)
                report_parts.append(content)
            else:
                # Otherwise, add the content directly
                report_parts.append(str(section_content))
            
            report_parts.append("")
        
        # Add details section
        if self.include_details and 'details' in analysis_results:
            report_parts.append("DETAILS")
            report_parts.append('-' * 7)
            report_parts.append("")
            
            details = analysis_results['details']
            if isinstance(details, str):
                report_parts.append(details)
            elif isinstance(details, dict):
                for key, value in details.items():
                    report_parts.append(f"{key}:")
                    report_parts.append("")
                    report_parts.append(str(value))
                    report_parts.append("")
            elif isinstance(details, list):
                for item in details:
                    if isinstance(item, dict) and 'title' in item and 'content' in item:
                        report_parts.append(f"{item['title']}:")
                        report_parts.append("")
                        report_parts.append(item['content'])
                        report_parts.append("")
                    else:
                        report_parts.append(str(item))
                        report_parts.append("")
        
        return "\n".join(report_parts)

