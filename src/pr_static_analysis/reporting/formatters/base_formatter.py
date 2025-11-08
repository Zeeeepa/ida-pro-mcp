"""
Base formatter for PR static analysis reports.

This module provides the BaseFormatter class that all formatters should inherit from.
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

class BaseFormatter(ABC):
    """
    Base class for report formatters.
    
    All formatters should inherit from this class and implement the format_report method.
    """
    
    @abstractmethod
    def format_report(self, results: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> str:
        """
        Format a report.
        
        Args:
            results: Analysis results
            metadata: Report metadata
            **kwargs: Additional formatting options
            
        Returns:
            Formatted report
        """
        pass
        
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format a single result.
        
        Args:
            result: Analysis result
            
        Returns:
            Formatted result
        """
        pass
        
    def format_section(self, title: str, content: str) -> str:
        """
        Format a section of the report.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            Formatted section
        """
        pass
        
    def _count_by_severity(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count results by severity.
        
        Args:
            results: Analysis results
            
        Returns:
            Dictionary mapping severity to count
        """
        counts = {}
        for result in results:
            severity = result.get("severity", "info")
            counts[severity] = counts.get(severity, 0) + 1
        return counts
        
    def _group_by_severity(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group results by severity.
        
        Args:
            results: Analysis results
            
        Returns:
            Dictionary mapping severity to list of results
        """
        grouped = {}
        for result in results:
            severity = result.get("severity", "info")
            if severity not in grouped:
                grouped[severity] = []
            grouped[severity].append(result)
        return grouped
        
    def _group_by_category(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group results by category.
        
        Args:
            results: Analysis results
            
        Returns:
            Dictionary mapping category to list of results
        """
        grouped = {}
        for result in results:
            category = result.get("category", "other")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(result)
        return grouped

