"""
HTML formatter for PR static analysis reports.

This module provides the HTMLFormatter class for generating HTML reports.
"""

from typing import Dict, List, Any, Optional
from .base_formatter import BaseFormatter

class HTMLFormatter(BaseFormatter):
    """Formatter for HTML reports."""
    
    def format_report(self, results: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> str:
        """
        Format a report as HTML.
        
        Args:
            results: Analysis results
            metadata: Report metadata
            **kwargs: Additional formatting options
                include_summary: Whether to include a summary section
                include_visualizations: Whether to include visualizations
            
        Returns:
            HTML report
        """
        # Get formatting options
        include_summary = kwargs.get("include_summary", True)
        include_visualizations = kwargs.get("include_visualizations", False)
        
        # Format the report header
        report = """<!DOCTYPE html>
<html>
<head>
    <title>PR Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 20px; }
        h3 { color: #777; }
        .result { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .critical { border-left: 5px solid #d9534f; }
        .error { border-left: 5px solid #f0ad4e; }
        .warning { border-left: 5px solid #f0ad4e; }
        .info { border-left: 5px solid #5bc0de; }
        .metadata { background-color: #f9f9f9; padding: 10px; border-radius: 5px; }
        .summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>PR Analysis Report</h1>
"""
        
        # Add metadata
        if metadata:
            report += """    <h2>Metadata</h2>
    <div class="metadata">
        <ul>
"""
            for key, value in metadata.items():
                report += f"            <li><strong>{key}:</strong> {value}</li>\n"
            report += """        </ul>
    </div>
"""
            
        # Add summary
        if include_summary:
            report += """    <h2>Summary</h2>
    <div class="summary">
        <ul>
"""
            severity_counts = self._count_by_severity(results)
            report += f"            <li><strong>Total Issues:</strong> {len(results)}</li>\n"
            for severity, count in severity_counts.items():
                report += f"            <li><strong>{severity.capitalize()}:</strong> {count} issue(s)</li>\n"
            report += """        </ul>
    </div>
"""
        
        # Add visualizations if requested
        if include_visualizations:
            report += """    <h2>Visualizations</h2>
    <div class="visualizations">
        <p>Visualizations would be included here in a real report.</p>
    </div>
"""
        
        # Group results by severity
        grouped = self._group_by_severity(results)
        
        # Add details for each severity
        for severity, items in grouped.items():
            report += f"    <h2>{severity.capitalize()} Issues</h2>\n"
            for item in items:
                report += self.format_result(item, severity)
            
        report += """</body>
</html>"""
        return report
        
    def format_result(self, result: Dict[str, Any], severity: str = "info") -> str:
        """
        Format a single result as HTML.
        
        Args:
            result: Analysis result
            severity: Result severity
            
        Returns:
            HTML-formatted result
        """
        rule_id = result.get("rule_id", "unknown")
        message = result.get("message", "No message")
        file_path = result.get("file_path")
        line = result.get("line")
        category = result.get("category", "other")
        
        location = ""
        if file_path:
            location = f"in <code>{file_path}</code>"
            if line:
                location += f" at line {line}"
                
        return f"""    <div class="result {severity}">
        <h3>{rule_id}</h3>
        <p>{message}</p>
        <p><strong>Category:</strong> {category}</p>
        <p><strong>Location:</strong> {location}</p>
    </div>
"""
        
    def format_section(self, title: str, content: str) -> str:
        """
        Format a section as HTML.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            HTML-formatted section
        """
        return f"""    <h2>{title}</h2>
    <div>
        {content}
    </div>
"""

