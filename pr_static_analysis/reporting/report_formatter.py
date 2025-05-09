"""
Report formatters for PR static analysis.

This module provides formatters for different output formats (Markdown, HTML, JSON).
"""
import json
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseReportFormatter(ABC):
    """Base class for report formatters."""
    
    @abstractmethod
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format a report.
        
        Args:
            report: The report to format
            
        Returns:
            Formatted report as a string
        """
        pass


class MarkdownReportFormatter(BaseReportFormatter):
    """Formatter for Markdown reports."""
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format a report as Markdown.
        
        Args:
            report: The report to format
            
        Returns:
            Markdown formatted report as a string
        """
        markdown = f"# PR Analysis Report for #{report['pr']['number']}\n\n"
        
        # Add PR information
        markdown += f"**PR:** [{report['pr']['title']}]({report['pr']['url']})\n"
        markdown += f"**Base:** `{report['pr']['base']}`\n"
        markdown += f"**Head:** `{report['pr']['head']}`\n\n"
        
        # Add summary
        summary = report['summary']
        markdown += "## Summary\n\n"
        markdown += f"- **Errors:** {summary['error_count']}\n"
        markdown += f"- **Warnings:** {summary['warning_count']}\n"
        markdown += f"- **Info:** {summary['info_count']}\n"
        markdown += f"- **Total:** {summary['total_count']}\n\n"
        
        # Add results
        if summary['total_count'] > 0:
            markdown += "## Issues\n\n"
            for result in report['results']:
                severity_icon = self._get_severity_icon(result['severity'])
                markdown += f"### {severity_icon} {result['rule_id']}: {result['message']}\n\n"
                
                if result.get('file'):
                    markdown += f"**File:** `{result['file']}`\n"
                    
                if result.get('line'):
                    markdown += f"**Line:** {result['line']}\n"
                    
                markdown += "\n"
        else:
            markdown += "No issues found! :white_check_mark:\n"
            
        return markdown
        
    def _get_severity_icon(self, severity: str) -> str:
        """Get an icon for a severity level.
        
        Args:
            severity: The severity level
            
        Returns:
            Icon string for the severity
        """
        if severity == "error":
            return ":x:"
        elif severity == "warning":
            return ":warning:"
        else:
            return ":information_source:"


class HTMLReportFormatter(BaseReportFormatter):
    """Formatter for HTML reports."""
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format a report as HTML.
        
        Args:
            report: The report to format
            
        Returns:
            HTML formatted report as a string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PR Analysis Report #{report['pr']['number']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #444; margin-top: 20px; }}
        h3 {{ margin-top: 15px; }}
        .pr-info {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .summary-item {{ padding: 10px; border-radius: 5px; text-align: center; flex: 1; }}
        .error {{ background-color: #ffebee; }}
        .warning {{ background-color: #fff8e1; }}
        .info {{ background-color: #e3f2fd; }}
        .total {{ background-color: #f5f5f5; }}
        .issue {{ border-left: 4px solid #ddd; padding-left: 15px; margin-bottom: 20px; }}
        .issue.error {{ border-left-color: #f44336; }}
        .issue.warning {{ border-left-color: #ff9800; }}
        .issue.info {{ border-left-color: #2196f3; }}
        .file-info {{ font-family: monospace; background-color: #f5f5f5; padding: 5px; }}
    </style>
</head>
<body>
    <h1>PR Analysis Report for #{report['pr']['number']}</h1>
    
    <div class="pr-info">
        <p><strong>PR:</strong> <a href="{report['pr']['url']}">{report['pr']['title']}</a></p>
        <p><strong>Base:</strong> <code>{report['pr']['base']}</code></p>
        <p><strong>Head:</strong> <code>{report['pr']['head']}</code></p>
    </div>
    
    <h2>Summary</h2>
    <div class="summary">
        <div class="summary-item error">
            <h3>Errors</h3>
            <p>{report['summary']['error_count']}</p>
        </div>
        <div class="summary-item warning">
            <h3>Warnings</h3>
            <p>{report['summary']['warning_count']}</p>
        </div>
        <div class="summary-item info">
            <h3>Info</h3>
            <p>{report['summary']['info_count']}</p>
        </div>
        <div class="summary-item total">
            <h3>Total</h3>
            <p>{report['summary']['total_count']}</p>
        </div>
    </div>
"""
        
        # Add results
        if report['summary']['total_count'] > 0:
            html += "<h2>Issues</h2>\n"
            
            for result in report['results']:
                severity = result['severity']
                html += f'<div class="issue {severity}">\n'
                html += f'<h3>{result["rule_id"]}: {result["message"]}</h3>\n'
                
                if result.get('file'):
                    html += f'<p class="file-info"><strong>File:</strong> {result["file"]}</p>\n'
                    
                if result.get('line'):
                    html += f'<p class="file-info"><strong>Line:</strong> {result["line"]}</p>\n'
                
                html += '</div>\n'
        else:
            html += "<p>No issues found! ✅</p>\n"
            
        html += """</body>
</html>"""
        
        return html


class JSONReportFormatter(BaseReportFormatter):
    """Formatter for JSON reports."""
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format a report as JSON.
        
        Args:
            report: The report to format
            
        Returns:
            JSON formatted report as a string
        """
        return json.dumps(report, indent=2)


class ReportFormatterFactory:
    """Factory for creating report formatters."""
    
    @staticmethod
    def create_formatter(format_type: str) -> BaseReportFormatter:
        """Create a report formatter for the specified format.
        
        Args:
            format_type: The format type (markdown, html, json)
            
        Returns:
            A report formatter instance
            
        Raises:
            ValueError: If the format type is not supported
        """
        format_type = format_type.lower()
        
        if format_type == 'markdown':
            return MarkdownReportFormatter()
        elif format_type == 'html':
            return HTMLReportFormatter()
        elif format_type == 'json':
            return JSONReportFormatter()
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

