"""
Report formatter for PR static analysis.

This module provides formatters for analysis reports.
"""

import json
from typing import Dict, List, Any, Optional
import os
import datetime

from ..core.analysis_context import PRAnalysisContext, AnalysisResult


class ReportFormatter:
    """
    Formatter for analysis reports.
    
    This class provides methods for formatting reports in different formats.
    """
    
    def __init__(self):
        """Initialize a new report formatter."""
        self.severity_icons = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
        }
        
    def format_as_markdown(self, context: PRAnalysisContext) -> str:
        """
        Format analysis results as Markdown.
        
        Args:
            context: The analysis context
            
        Returns:
            A Markdown string
        """
        results = context.results
        
        if not results:
            return "# PR Analysis Report\n\nNo issues found!\n"
            
        # Group results by file
        results_by_file: Dict[str, List[AnalysisResult]] = {}
        for result in results:
            file = result.file or "General"
            if file not in results_by_file:
                results_by_file[file] = []
            results_by_file[file].append(result)
            
        # Format report
        report = "# PR Analysis Report\n\n"
        
        # Add PR info
        report += "## PR Information\n\n"
        report += f"- **PR ID:** {context.pr_id}\n"
        report += f"- **Repository:** {context.repo_name}\n"
        report += f"- **Base Branch:** {context.base_branch}\n"
        report += f"- **Head Branch:** {context.head_branch}\n"
        
        if context.start_time and context.end_time:
            duration = context.get_analysis_duration()
            report += f"- **Analysis Duration:** {duration:.2f} seconds\n"
            
        report += "\n"
        
        # Add summary
        errors = len([r for r in results if r.severity == "error"])
        warnings = len([r for r in results if r.severity == "warning"])
        infos = len([r for r in results if r.severity == "info"])
        
        report += "## Summary\n\n"
        report += f"- {self.severity_icons['error']} **Errors:** {errors}\n"
        report += f"- {self.severity_icons['warning']} **Warnings:** {warnings}\n"
        report += f"- {self.severity_icons['info']} **Info:** {infos}\n\n"
        
        # Add results by file
        for file, file_results in results_by_file.items():
            if file == "General":
                report += "## General Issues\n\n"
            else:
                report += f"## File: `{file}`\n\n"
                
            for result in file_results:
                icon = self.severity_icons.get(result.severity, "")
                location = f"line {result.line}" if result.line else ""
                
                report += f"### {icon} {result.rule_name} {location}\n\n"
                report += f"{result.message}\n\n"
                
                if result.suggested_fix:
                    report += "**Suggested Fix:**\n\n"
                    report += f"```\n{result.suggested_fix}\n```\n\n"
                    
        return report
        
    def format_as_html(self, context: PRAnalysisContext) -> str:
        """
        Format analysis results as HTML.
        
        Args:
            context: The analysis context
            
        Returns:
            An HTML string
        """
        results = context.results
        
        if not results:
            return "<html><body><h1>PR Analysis Report</h1><p>No issues found!</p></body></html>"
            
        # Group results by file
        results_by_file: Dict[str, List[AnalysisResult]] = {}
        for result in results:
            file = result.file or "General"
            if file not in results_by_file:
                results_by_file[file] = []
            results_by_file[file].append(result)
            
        # Format report
        report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PR Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #555; margin-top: 20px; }
                h3 { color: #777; }
                .error { color: #d9534f; }
                .warning { color: #f0ad4e; }
                .info { color: #5bc0de; }
                .file { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
                .suggested-fix { background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h1>PR Analysis Report</h1>
        """
        
        # Add PR info
        report += "<h2>PR Information</h2>"
        report += "<ul>"
        report += f"<li><strong>PR ID:</strong> {context.pr_id}</li>"
        report += f"<li><strong>Repository:</strong> {context.repo_name}</li>"
        report += f"<li><strong>Base Branch:</strong> {context.base_branch}</li>"
        report += f"<li><strong>Head Branch:</strong> {context.head_branch}</li>"
        
        if context.start_time and context.end_time:
            duration = context.get_analysis_duration()
            report += f"<li><strong>Analysis Duration:</strong> {duration:.2f} seconds</li>"
            
        report += "</ul>"
        
        # Add summary
        errors = len([r for r in results if r.severity == "error"])
        warnings = len([r for r in results if r.severity == "warning"])
        infos = len([r for r in results if r.severity == "info"])
        
        report += "<h2>Summary</h2>"
        report += "<ul>"
        report += f"<li class='error'><strong>Errors:</strong> {errors}</li>"
        report += f"<li class='warning'><strong>Warnings:</strong> {warnings}</li>"
        report += f"<li class='info'><strong>Info:</strong> {infos}</li>"
        report += "</ul>"
        
        # Add results by file
        for file, file_results in results_by_file.items():
            if file == "General":
                report += "<h2>General Issues</h2>"
            else:
                report += f"<h2>File: <code class='file'>{file}</code></h2>"
                
            for result in file_results:
                severity_class = result.severity
                location = f"line {result.line}" if result.line else ""
                
                report += f"<h3 class='{severity_class}'>{result.rule_name} {location}</h3>"
                report += f"<p>{result.message}</p>"
                
                if result.suggested_fix:
                    report += "<p><strong>Suggested Fix:</strong></p>"
                    report += f"<div class='suggested-fix'>{result.suggested_fix}</div>"
                    
        report += """
        </body>
        </html>
        """
        
        return report
        
    def format_as_json(self, context: PRAnalysisContext) -> str:
        """
        Format analysis results as JSON.
        
        Args:
            context: The analysis context
            
        Returns:
            A JSON string
        """
        report = {
            "pr_id": context.pr_id,
            "repo_name": context.repo_name,
            "base_branch": context.base_branch,
            "head_branch": context.head_branch,
            "status": context.status.value,
            "start_time": context.start_time.isoformat() if context.start_time else None,
            "end_time": context.end_time.isoformat() if context.end_time else None,
            "duration": context.get_analysis_duration(),
            "results": [self._format_result(r) for r in context.results],
            "summary": self._generate_summary(context.results),
        }
        
        return json.dumps(report, indent=2)
        
    def _format_result(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        Format an analysis result for a report.
        
        Args:
            result: The analysis result to format
            
        Returns:
            A dictionary with the formatted result
        """
        return {
            "rule_id": result.rule_id,
            "rule_name": result.rule_name,
            "severity": result.severity,
            "message": result.message,
            "file": result.file,
            "line": result.line,
            "column": result.column,
            "suggested_fix": result.suggested_fix,
            "metadata": result.metadata,
        }
        
    def _generate_summary(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Generate a summary of analysis results.
        
        Args:
            results: The analysis results to summarize
            
        Returns:
            A dictionary with the summary data
        """
        # Count issues by severity
        errors = len([r for r in results if r.severity == "error"])
        warnings = len([r for r in results if r.severity == "warning"])
        infos = len([r for r in results if r.severity == "info"])
        
        # Count issues by rule
        issues_by_rule: Dict[str, int] = {}
        for result in results:
            rule_id = result.rule_id
            if rule_id not in issues_by_rule:
                issues_by_rule[rule_id] = 0
            issues_by_rule[rule_id] += 1
            
        # Count issues by file
        issues_by_file: Dict[str, int] = {}
        for result in results:
            file = result.file or "General"
            if file not in issues_by_file:
                issues_by_file[file] = 0
            issues_by_file[file] += 1
            
        return {
            "total_issues": len(results),
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "issues_by_rule": issues_by_rule,
            "issues_by_file": issues_by_file,
        }

