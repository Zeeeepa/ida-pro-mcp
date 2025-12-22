"""
Markdown Formatter Module

This module provides a formatter for converting analysis results into Markdown format.
"""

from typing import Any, Dict, Optional, List

from .base_formatter import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """
    Formatter for converting analysis results into Markdown format.
    
    This formatter generates a Markdown report from analysis results.
    It supports customization of the report structure and content.
    """
    
    def __init__(
        self,
        include_summary: bool = True,
        include_details: bool = True,
        include_issues: bool = True,
        include_files: bool = True,
        include_metrics: bool = True,
        custom_sections: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new MarkdownFormatter.
        
        Args:
            include_summary: Whether to include a summary section
            include_details: Whether to include a details section
            include_issues: Whether to include an issues section
            include_files: Whether to include a files section
            include_metrics: Whether to include a metrics section
            custom_sections: Optional dictionary of custom sections to include
        """
        self.include_summary = include_summary
        self.include_details = include_details
        self.include_issues = include_issues
        self.include_files = include_files
        self.include_metrics = include_metrics
        self.custom_sections = custom_sections or {}
        
    def format(
        self, 
        analysis_results: Dict[str, Any], 
        visualizations: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Format analysis results into a Markdown report.
        
        Args:
            analysis_results: Analysis results to format
            visualizations: Optional dictionary of visualization data
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            The formatted report as a Markdown string
        """
        report_parts = []
        
        # Add title
        title = kwargs.get('title', 'PR Static Analysis Report')
        report_parts.append(f"# {title}")
        report_parts.append("")
        
        # Add summary section
        if self.include_summary and 'summary' in analysis_results:
            report_parts.append("## Summary")
            report_parts.append("")
            report_parts.append(analysis_results['summary'])
            report_parts.append("")
        
        # Add issues section
        if self.include_issues and 'issues' in analysis_results:
            report_parts.append("## Issues")
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
                    
                    report_parts.append(f"- **[{severity}]**{location}: {message}")
            
            report_parts.append("")
        
        # Add files section
        if self.include_files and any(k in analysis_results for k in ['files_added', 'files_modified', 'files_removed']):
            report_parts.append("## Files")
            report_parts.append("")
            
            files_added = analysis_results.get('files_added', [])
            files_modified = analysis_results.get('files_modified', [])
            files_removed = analysis_results.get('files_removed', [])
            
            if files_added:
                report_parts.append("### Files Added")
                report_parts.append("")
                for file in sorted(files_added):
                    report_parts.append(f"- `{file}`")
                report_parts.append("")
            
            if files_modified:
                report_parts.append("### Files Modified")
                report_parts.append("")
                for file in sorted(files_modified):
                    report_parts.append(f"- `{file}`")
                report_parts.append("")
            
            if files_removed:
                report_parts.append("### Files Removed")
                report_parts.append("")
                for file in sorted(files_removed):
                    report_parts.append(f"- `{file}`")
                report_parts.append("")
        
        # Add metrics section
        if self.include_metrics and 'metrics' in analysis_results:
            report_parts.append("## Metrics")
            report_parts.append("")
            
            metrics = analysis_results['metrics']
            for key, value in metrics.items():
                # Format the key for better readability
                formatted_key = key.replace('_', ' ').title()
                report_parts.append(f"- **{formatted_key}**: {value}")
            
            report_parts.append("")
        
        # Add visualizations
        if visualizations:
            report_parts.append("## Visualizations")
            report_parts.append("")
            
            for viz_name, viz_data in visualizations.items():
                if isinstance(viz_data, str):
                    # If the visualization is a string (e.g., a URL or embedded image), add it directly
                    report_parts.append(f"### {viz_name.replace('_', ' ').title()}")
                    report_parts.append("")
                    report_parts.append(viz_data)
                    report_parts.append("")
            
        # Add custom sections
        for section_name, section_content in self.custom_sections.items():
            report_parts.append(f"## {section_name}")
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
            report_parts.append("## Details")
            report_parts.append("")
            
            details = analysis_results['details']
            if isinstance(details, str):
                report_parts.append(details)
            elif isinstance(details, dict):
                for key, value in details.items():
                    report_parts.append(f"### {key}")
                    report_parts.append("")
                    report_parts.append(str(value))
                    report_parts.append("")
            elif isinstance(details, list):
                for item in details:
                    if isinstance(item, dict) and 'title' in item and 'content' in item:
                        report_parts.append(f"### {item['title']}")
                        report_parts.append("")
                        report_parts.append(item['content'])
                        report_parts.append("")
                    else:
                        report_parts.append(str(item))
                        report_parts.append("")
            
        return "\n".join(report_parts)

