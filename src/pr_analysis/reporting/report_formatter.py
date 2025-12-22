"""
Report formatters for the PR static analysis system.

This module contains formatters for different output formats (HTML, Markdown, JSON).
"""

import json
from typing import Any, Dict, List, Optional
import html
import datetime

from .report_generator import Report, ReportResult, ReportSection


class BaseFormatter:
    """Base class for report formatters."""
    
    def format_report(self, report: Report) -> str:
        """
        Format a report.
        
        Args:
            report: The report to format.
            
        Returns:
            The formatted report as a string.
        """
        raise NotImplementedError("Subclasses must implement format_report")
    
    def format_result(self, result: ReportResult) -> str:
        """
        Format a single result.
        
        Args:
            result: The result to format.
            
        Returns:
            The formatted result as a string.
        """
        raise NotImplementedError("Subclasses must implement format_result")
    
    def format_section(self, section: ReportSection) -> str:
        """
        Format a section.
        
        Args:
            section: The section to format.
            
        Returns:
            The formatted section as a string.
        """
        raise NotImplementedError("Subclasses must implement format_section")


class HTMLFormatter(BaseFormatter):
    """Formatter for HTML output."""
    
    def format_report(self, report: Report) -> str:
        """
        Format a report as HTML.
        
        Args:
            report: The report to format.
            
        Returns:
            The formatted report as an HTML string.
        """
        template = self.get_html_template()
        
        # Format results
        results_html = ""
        for result in report.results:
            results_html += self.format_result(result)
        
        # Format sections
        sections_html = ""
        for section in sorted(report.sections, key=lambda s: s.order):
            sections_html += self.format_section(section)
        
        # Format metadata
        metadata_html = "<dl class='metadata'>"
        for key, value in report.metadata.items():
            metadata_html += f"<dt>{html.escape(str(key))}</dt><dd>{html.escape(str(value))}</dd>"
        metadata_html += "</dl>"
        
        # Replace placeholders in template
        html_report = template.replace("{{title}}", html.escape(report.title))
        html_report = html_report.replace("{{summary}}", report.summary)
        html_report = html_report.replace("{{results}}", results_html)
        html_report = html_report.replace("{{sections}}", sections_html)
        html_report = html_report.replace("{{metadata}}", metadata_html)
        html_report = html_report.replace("{{created_at}}", report.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        return html_report
    
    def format_result(self, result: ReportResult) -> str:
        """
        Format a single result as HTML.
        
        Args:
            result: The result to format.
            
        Returns:
            The formatted result as an HTML string.
        """
        severity_class = f"severity-{result.severity.lower()}"
        
        html_result = f"<div class='result {severity_class}'>"
        html_result += f"<div class='result-header'>"
        html_result += f"<span class='severity'>{html.escape(result.severity.upper())}</span>"
        html_result += f"<span class='category'>{html.escape(result.category)}</span>"
        if result.rule_id:
            html_result += f"<span class='rule-id'>{html.escape(result.rule_id)}</span>"
        html_result += "</div>"
        
        html_result += f"<div class='message'>{html.escape(result.message)}</div>"
        
        if result.file_path:
            html_result += "<div class='location'>"
            html_result += f"<span class='file'>{html.escape(result.file_path)}</span>"
            if result.line_number:
                html_result += f"<span class='line'>Line {result.line_number}</span>"
            if result.column:
                html_result += f"<span class='column'>Column {result.column}</span>"
            html_result += "</div>"
        
        if result.code_snippet:
            html_result += f"<pre class='code-snippet'>{html.escape(result.code_snippet)}</pre>"
        
        html_result += "</div>"
        
        return html_result
    
    def format_section(self, section: ReportSection) -> str:
        """
        Format a section as HTML.
        
        Args:
            section: The section to format.
            
        Returns:
            The formatted section as an HTML string.
        """
        html_section = f"<section class='report-section'>"
        html_section += f"<h2>{html.escape(section.title)}</h2>"
        html_section += f"<div class='section-content'>{section.content}</div>"
        html_section += "</section>"
        
        return html_section
    
    def get_html_template(self) -> str:
        """
        Get the HTML template for reports.
        
        Returns:
            The HTML template as a string.
        """
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .report-header {
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        .report-summary {
            margin-bottom: 30px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .report-section {
            margin-bottom: 30px;
        }
        .result {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 5px;
            border-left: 5px solid #ddd;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .severity {
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 3px;
            color: white;
        }
        .severity-critical {
            border-left-color: #d9534f;
        }
        .severity-critical .severity {
            background-color: #d9534f;
        }
        .severity-error {
            border-left-color: #f0ad4e;
        }
        .severity-error .severity {
            background-color: #f0ad4e;
        }
        .severity-warning {
            border-left-color: #5bc0de;
        }
        .severity-warning .severity {
            background-color: #5bc0de;
        }
        .severity-info {
            border-left-color: #5cb85c;
        }
        .severity-info .severity {
            background-color: #5cb85c;
        }
        .category, .rule-id {
            color: #777;
            font-size: 0.9em;
        }
        .message {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .location {
            font-family: monospace;
            margin-bottom: 10px;
            color: #666;
        }
        .code-snippet {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
        .metadata {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
            color: #777;
        }
        .metadata dt {
            font-weight: bold;
            float: left;
            clear: left;
            width: 180px;
        }
        .metadata dd {
            margin-left: 200px;
            margin-bottom: 10px;
        }
        .report-footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
            color: #777;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="report-header">
        <h1>{{title}}</h1>
        <p>Generated on {{created_at}}</p>
    </div>
    
    <div class="report-summary">
        {{summary}}
    </div>
    
    <div class="report-results">
        <h2>Results</h2>
        {{results}}
    </div>
    
    {{sections}}
    
    {{metadata}}
    
    <div class="report-footer">
        <p>PR Static Analysis Report</p>
    </div>
</body>
</html>
"""


class MarkdownFormatter(BaseFormatter):
    """Formatter for Markdown output."""
    
    def format_report(self, report: Report) -> str:
        """
        Format a report as Markdown.
        
        Args:
            report: The report to format.
            
        Returns:
            The formatted report as a Markdown string.
        """
        template = self.get_markdown_template()
        
        # Format results
        results_md = ""
        for result in report.results:
            results_md += self.format_result(result)
        
        # Format sections
        sections_md = ""
        for section in sorted(report.sections, key=lambda s: s.order):
            sections_md += self.format_section(section)
        
        # Format metadata
        metadata_md = "## Metadata\n\n"
        for key, value in report.metadata.items():
            metadata_md += f"- **{key}**: {value}\n"
        
        # Replace placeholders in template
        md_report = template.replace("{{title}}", report.title)
        md_report = md_report.replace("{{summary}}", report.summary)
        md_report = md_report.replace("{{results}}", results_md)
        md_report = md_report.replace("{{sections}}", sections_md)
        md_report = md_report.replace("{{metadata}}", metadata_md)
        md_report = md_report.replace("{{created_at}}", report.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        return md_report
    
    def format_result(self, result: ReportResult) -> str:
        """
        Format a single result as Markdown.
        
        Args:
            result: The result to format.
            
        Returns:
            The formatted result as a Markdown string.
        """
        md_result = f"### {result.severity.upper()}: {result.message}\n\n"
        
        md_result += f"- **Category**: {result.category}\n"
        if result.rule_id:
            md_result += f"- **Rule ID**: {result.rule_id}\n"
        
        if result.file_path:
            md_result += f"- **File**: {result.file_path}\n"
            if result.line_number:
                md_result += f"- **Line**: {result.line_number}\n"
            if result.column:
                md_result += f"- **Column**: {result.column}\n"
        
        if result.code_snippet:
            md_result += "\n```\n" + result.code_snippet + "\n```\n"
        
        md_result += "\n"
        
        return md_result
    
    def format_section(self, section: ReportSection) -> str:
        """
        Format a section as Markdown.
        
        Args:
            section: The section to format.
            
        Returns:
            The formatted section as a Markdown string.
        """
        md_section = f"## {section.title}\n\n"
        md_section += f"{section.content}\n\n"
        
        return md_section
    
    def get_markdown_template(self) -> str:
        """
        Get the Markdown template for reports.
        
        Returns:
            The Markdown template as a string.
        """
        return """# {{title}}

*Generated on {{created_at}}*

{{summary}}

## Results

{{results}}

{{sections}}

{{metadata}}

---
*PR Static Analysis Report*
"""


class JSONFormatter(BaseFormatter):
    """Formatter for JSON output."""
    
    def format_report(self, report: Report) -> str:
        """
        Format a report as JSON.
        
        Args:
            report: The report to format.
            
        Returns:
            The formatted report as a JSON string.
        """
        # Convert report to a dictionary
        report_dict = {
            "title": report.title,
            "summary": report.summary,
            "results": [self._result_to_dict(result) for result in report.results],
            "sections": [self._section_to_dict(section) for section in report.sections],
            "metadata": report.metadata,
            "created_at": report.created_at.isoformat(),
        }
        
        # Convert to JSON
        return json.dumps(report_dict, indent=2)
    
    def format_result(self, result: ReportResult) -> str:
        """
        Format a single result as JSON.
        
        Args:
            result: The result to format.
            
        Returns:
            The formatted result as a JSON string.
        """
        result_dict = self._result_to_dict(result)
        return json.dumps(result_dict, indent=2)
    
    def format_section(self, section: ReportSection) -> str:
        """
        Format a section as JSON.
        
        Args:
            section: The section to format.
            
        Returns:
            The formatted section as a JSON string.
        """
        section_dict = self._section_to_dict(section)
        return json.dumps(section_dict, indent=2)
    
    def _result_to_dict(self, result: ReportResult) -> Dict[str, Any]:
        """
        Convert a ReportResult to a dictionary.
        
        Args:
            result: The result to convert.
            
        Returns:
            A dictionary representation of the result.
        """
        return {
            "message": result.message,
            "severity": result.severity,
            "category": result.category,
            "file_path": result.file_path,
            "line_number": result.line_number,
            "column": result.column,
            "code_snippet": result.code_snippet,
            "rule_id": result.rule_id,
            "metadata": result.metadata,
        }
    
    def _section_to_dict(self, section: ReportSection) -> Dict[str, Any]:
        """
        Convert a ReportSection to a dictionary.
        
        Args:
            section: The section to convert.
            
        Returns:
            A dictionary representation of the section.
        """
        return {
            "title": section.title,
            "content": section.content,
            "order": section.order,
            "metadata": section.metadata,
        }

