"""
Report generator for PR static analysis.

This module provides functionality to generate analysis reports from rule results.
"""
from typing import List, Dict, Any
from datetime import datetime


class ReportGenerator:
    """Generator for analysis reports."""
    
    def generate_report(self, results, pr_context):
        """Generate a report from analysis results.
        
        Args:
            results: List of analysis results from rule execution
            pr_context: Context information about the PR being analyzed
            
        Returns:
            Dict containing the formatted report
        """
        report = {
            "pr": {
                "number": pr_context.number,
                "title": pr_context.title,
                "url": pr_context.html_url,
                "base": pr_context.base.ref,
                "head": pr_context.head.ref,
            },
            "summary": self._generate_summary(results),
            "results": [result.to_dict() for result in results],
            "timestamp": self._get_timestamp(),
        }
        return report
        
    def _generate_summary(self, results):
        """Generate a summary of the analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            Dict containing summary statistics
        """
        error_count = len([r for r in results if r.severity == "error"])
        warning_count = len([r for r in results if r.severity == "warning"])
        info_count = len([r for r in results if r.severity == "info"])
        
        return {
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "total_count": len(results),
            "has_errors": error_count > 0,
            "has_warnings": warning_count > 0,
        }
        
    def _get_timestamp(self):
        """Get the current timestamp.
        
        Returns:
            ISO formatted timestamp string
        """
        return datetime.utcnow().isoformat()

