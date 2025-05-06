"""
Text formatter for PR static analysis reports.

This module provides the TextFormatter class for generating plain text reports.
"""

from typing import Dict, List, Any, Optional
from .base_formatter import BaseFormatter

class TextFormatter(BaseFormatter):
    """Formatter for plain text reports."""
    
    def format_report(self, results: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> str:
        """
        Format a report as plain text.
        
        Args:
            results: Analysis results
            metadata: Report metadata
            **kwargs: Additional formatting options
                include_summary: Whether to include a summary section
            
        Returns:
            Plain text report
        """
        # Get formatting options
        include_summary = kwargs.get("include_summary", True)
        
        # Format the report header
        report = "PR ANALYSIS REPORT\n"
        report += "=================\n\n"
        
        # Add metadata
        if metadata:
            report += "METADATA\n"
            report += "--------\n\n"
            for key, value in metadata.items():
                report += f"{key}: {value}\n"
            report += "\n"
            
        # Add summary
        if include_summary:
            report += "SUMMARY\n"
            report += "-------\n\n"
            severity_counts = self._count_by_severity(results)
            report += f"Total Issues: {len(results)}\n"
            for severity, count in severity_counts.items():
                report += f"{severity.capitalize()}: {count} issue(s)\n"
            report += "\n"
        
        # Group results by severity
        grouped = self._group_by_severity(results)
        
        # Add details for each severity
        for severity, items in grouped.items():
            report += f"{severity.upper()} ISSUES\n"
            report += "-" * (len(severity) + 7) + "\n\n"
            for item in items:
                report += self.format_result(item)
            report += "\n"
            
        return report
        
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format a single result as plain text.
        
        Args:
            result: Analysis result
            
        Returns:
            Plain text formatted result
        """
        rule_id = result.get("rule_id", "unknown")
        message = result.get("message", "No message")
        file_path = result.get("file_path")
        line = result.get("line")
        category = result.get("category", "other")
        
        location = ""
        if file_path:
            location = f"in {file_path}"
            if line:
                location += f" at line {line}"
                
        formatted = f"{rule_id}\n"
        formatted += "-" * len(rule_id) + "\n"
        formatted += f"Message: {message}\n"
        formatted += f"Category: {category}\n"
        formatted += f"Location: {location}\n\n"
        
        return formatted
        
    def format_section(self, title: str, content: str) -> str:
        """
        Format a section as plain text.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            Plain text formatted section
        """
        formatted = f"{title.upper()}\n"
        formatted += "-" * len(title) + "\n\n"
        formatted += f"{content}\n\n"
        
        return formatted

