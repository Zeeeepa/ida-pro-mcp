"""
Markdown formatter for PR static analysis reports.

This module provides the MarkdownFormatter class for generating Markdown reports.
"""

from typing import Dict, List, Any, Optional
from .base_formatter import BaseFormatter

class MarkdownFormatter(BaseFormatter):
    """Formatter for Markdown reports."""
    
    def format_report(self, results: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> str:
        """
        Format a report as Markdown.
        
        Args:
            results: Analysis results
            metadata: Report metadata
            **kwargs: Additional formatting options
                include_summary: Whether to include a summary section
                include_visualizations: Whether to include visualizations
            
        Returns:
            Markdown report
        """
        # Get formatting options
        include_summary = kwargs.get("include_summary", True)
        include_visualizations = kwargs.get("include_visualizations", False)
        
        # Format the report header
        report = "# PR Analysis Report\n\n"
        
        # Add metadata
        if metadata:
            report += "## Metadata\n\n"
            for key, value in metadata.items():
                report += f"- **{key}**: {value}\n"
            report += "\n"
            
        # Add summary
        if include_summary:
            report += "## Summary\n\n"
            severity_counts = self._count_by_severity(results)
            report += f"- **Total Issues**: {len(results)}\n"
            for severity, count in severity_counts.items():
                report += f"- **{severity.capitalize()}**: {count} issue(s)\n"
            report += "\n"
        
        # Add visualizations if requested
        if include_visualizations:
            report += "## Visualizations\n\n"
            report += "Visualizations would be included here in a real report.\n\n"
        
        # Group results by severity
        grouped = self._group_by_severity(results)
        
        # Add details for each severity
        for severity, items in grouped.items():
            report += f"## {severity.capitalize()} Issues\n\n"
            for item in items:
                report += self.format_result(item)
            report += "\n"
            
        return report
        
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format a single result as Markdown.
        
        Args:
            result: Analysis result
            
        Returns:
            Markdown-formatted result
        """
        rule_id = result.get("rule_id", "unknown")
        message = result.get("message", "No message")
        file_path = result.get("file_path")
        line = result.get("line")
        category = result.get("category", "other")
        
        location = ""
        if file_path:
            location = f"in `{file_path}`"
            if line:
                location += f" at line {line}"
                
        return f"### {rule_id}\n\n{message}\n\n**Category**: {category}\n\n**Location**: {location}\n\n"
        
    def format_section(self, title: str, content: str) -> str:
        """
        Format a section as Markdown.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            Markdown-formatted section
        """
        return f"## {title}\n\n{content}\n\n"

