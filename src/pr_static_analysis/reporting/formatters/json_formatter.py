"""
JSON formatter for PR static analysis reports.

This module provides the JSONFormatter class for generating JSON reports.
"""

from typing import Dict, List, Any, Optional
import json
from .base_formatter import BaseFormatter

class JSONFormatter(BaseFormatter):
    """Formatter for JSON reports."""
    
    def format_report(self, results: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> str:
        """
        Format a report as JSON.
        
        Args:
            results: Analysis results
            metadata: Report metadata
            **kwargs: Additional formatting options
            
        Returns:
            JSON report
        """
        # Get formatting options
        include_summary = kwargs.get("include_summary", True)
        
        # Create the report structure
        report = {
            "metadata": metadata,
            "results": results,
        }
        
        # Add summary if requested
        if include_summary:
            report["summary"] = self._generate_summary(results)
        
        return json.dumps(report, indent=2)
        
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format a single result as JSON.
        
        Args:
            result: Analysis result
            
        Returns:
            JSON-formatted result
        """
        return json.dumps(result, indent=2)
        
    def format_section(self, title: str, content: str) -> str:
        """
        Format a section as JSON.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            JSON-formatted section
        """
        section = {
            "title": title,
            "content": content,
        }
        return json.dumps(section, indent=2)
        
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the results.
        
        Args:
            results: Analysis results
            
        Returns:
            Summary dictionary
        """
        severity_counts = self._count_by_severity(results)
        category_counts = {}
        
        for result in results:
            category = result.get("category", "other")
            category_counts[category] = category_counts.get(category, 0) + 1
            
        return {
            "total": len(results),
            "by_severity": severity_counts,
            "by_category": category_counts
        }

