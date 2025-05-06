"""
Report generator for PR static analysis.

This module provides a generator for analysis reports.
"""

import json
from typing import Dict, List, Any, Optional
import os
import datetime

from ..core.analysis_context import PRAnalysisContext, AnalysisResult


class ReportGenerator:
    """
    Generator for analysis reports.
    
    This class provides methods for generating reports from analysis results.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize a new report generator.
        
        Args:
            output_dir: The directory to output reports to
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_json_report(self, context: PRAnalysisContext) -> Dict[str, Any]:
        """
        Generate a JSON report from analysis results.
        
        Args:
            context: The analysis context
            
        Returns:
            A dictionary with the report data
        """
        return {
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
        
    def save_json_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save a JSON report to a file.
        
        Args:
            report: The report to save
            filename: Optional filename to save to
            
        Returns:
            The path to the saved report
        """
        if not filename:
            # Generate a filename based on the PR ID and timestamp
            pr_id = report.get("pr_id", "unknown")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{pr_id}_{timestamp}.json"
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
            
        return filepath
        
    def generate_and_save_report(self, context: PRAnalysisContext, 
                               format: str = "json") -> str:
        """
        Generate and save a report.
        
        Args:
            context: The analysis context
            format: The format of the report ("json", "html", "markdown")
            
        Returns:
            The path to the saved report
        """
        if format == "json":
            report = self.generate_json_report(context)
            return self.save_json_report(report)
        elif format == "html":
            # Placeholder for HTML report generation
            report = self.generate_json_report(context)
            return self.save_json_report(report, f"report_{context.pr_id}.html")
        elif format == "markdown":
            # Placeholder for Markdown report generation
            report = self.generate_json_report(context)
            return self.save_json_report(report, f"report_{context.pr_id}.md")
        else:
            raise ValueError(f"Unsupported report format: {format}")

