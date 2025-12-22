"""
Report generator for PR static analysis.

This module provides the ReportGenerator class for generating reports from analysis results.
"""

from typing import Dict, List, Any, Optional
import logging

class ReportGenerator:
    """
    Generator for analysis reports.
    
    This class collects and organizes analysis results and generates reports.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.logger = logging.getLogger(__name__)
        self.formatters = {}
        self.results = []
        self.metadata = {}
        self.config = None
        
    def register_formatter(self, format_type: str, formatter) -> None:
        """
        Register a formatter for a specific format type.
        
        Args:
            format_type: Format type (e.g., "markdown", "html")
            formatter: Formatter instance
        """
        self.formatters[format_type] = formatter
        
    def add_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Add analysis results.
        
        Args:
            results: List of analysis results
        """
        self.results.extend(results)
        
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set metadata for the report.
        
        Args:
            metadata: Report metadata
        """
        self.metadata = metadata
        
    def apply_config(self, config) -> None:
        """
        Apply configuration to the report generator.
        
        Args:
            config: Report configuration
        """
        self.config = config
        
    def generate_report(self, format_type: str = "markdown") -> str:
        """
        Generate a report in the specified format.
        
        Args:
            format_type: Format type (e.g., "markdown", "html")
            
        Returns:
            Formatted report
        """
        formatter = self.formatters.get(format_type)
        if not formatter:
            raise ValueError(f"No formatter registered for format type: {format_type}")
        
        # Apply configuration if available
        if self.config:
            # Filter results by severity if configured
            severity_filter = self.config.get("severity_filter")
            if severity_filter:
                filtered_results = [r for r in self.results if r.get("severity") in severity_filter]
            else:
                filtered_results = self.results
                
            # Limit the number of results if configured
            max_results = self.config.get("max_results")
            if max_results and max_results > 0:
                filtered_results = filtered_results[:max_results]
                
            # Generate the report with filtered results
            return formatter.format_report(
                filtered_results, 
                self.metadata,
                include_summary=self.config.get("include_summary", True),
                include_visualizations=self.config.get("include_visualizations", False)
            )
        else:
            # Generate the report with all results
            return formatter.format_report(self.results, self.metadata)
        
    def filter_results_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Filter results by severity.
        
        Args:
            severity: Severity level
            
        Returns:
            Filtered results
        """
        return [r for r in self.results if r.get("severity") == severity]
        
    def filter_results_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Filter results by category.
        
        Args:
            category: Result category
            
        Returns:
            Filtered results
        """
        return [r for r in self.results if r.get("category") == category]
        
    def sort_results(self, key: str) -> List[Dict[str, Any]]:
        """
        Sort results by a specific key.
        
        Args:
            key: Key to sort by
            
        Returns:
            Sorted results
        """
        return sorted(self.results, key=lambda r: r.get(key, ""))

