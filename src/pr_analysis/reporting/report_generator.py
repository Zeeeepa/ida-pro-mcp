"""
Report generator for the PR static analysis system.

This module contains the ReportGenerator class, which is responsible for collecting
and organizing analysis results, and generating reports based on those results.
"""

from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
import datetime


@dataclass
class ReportSection:
    """A section of a report."""
    title: str
    content: str
    order: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportResult:
    """A single result in a report."""
    message: str
    severity: str  # "critical", "error", "warning", "info"
    category: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    """A complete report."""
    title: str
    summary: str
    results: List[ReportResult] = field(default_factory=list)
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)


class ReportGenerator:
    """
    Generator for PR static analysis reports.
    
    This class is responsible for collecting and organizing analysis results,
    and generating reports based on those results.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.results = []
        self.report_options = {}
        self.report_metadata = {}
        self.custom_sections = []
    
    def collect_results(self, context) -> List[ReportResult]:
        """
        Collect results from the analysis context.
        
        Args:
            context: The analysis context containing results.
            
        Returns:
            A list of ReportResult objects.
        """
        # Extract results from the context
        # This implementation depends on the structure of the analysis context
        results = []
        
        # Assuming context has a get_results() method that returns a list of results
        if hasattr(context, 'get_results') and callable(context.get_results):
            raw_results = context.get_results()
            
            for result in raw_results:
                # Convert raw result to ReportResult
                report_result = ReportResult(
                    message=result.get('message', ''),
                    severity=result.get('severity', 'info'),
                    category=result.get('category', 'general'),
                    file_path=result.get('file_path'),
                    line_number=result.get('line_number'),
                    column=result.get('column'),
                    code_snippet=result.get('code_snippet'),
                    rule_id=result.get('rule_id'),
                    metadata=result.get('metadata', {})
                )
                results.append(report_result)
        
        self.results = results
        return results
    
    def filter_results_by_severity(self, severity: Union[str, List[str]]) -> List[ReportResult]:
        """
        Filter results by severity.
        
        Args:
            severity: A severity level or list of severity levels to filter by.
            
        Returns:
            A list of filtered ReportResult objects.
        """
        if isinstance(severity, str):
            severity = [severity]
        
        return [result for result in self.results if result.severity in severity]
    
    def filter_results_by_category(self, category: Union[str, List[str]]) -> List[ReportResult]:
        """
        Filter results by category.
        
        Args:
            category: A category or list of categories to filter by.
            
        Returns:
            A list of filtered ReportResult objects.
        """
        if isinstance(category, str):
            category = [category]
        
        return [result for result in self.results if result.category in category]
    
    def sort_results(self, key: Union[str, Callable]) -> List[ReportResult]:
        """
        Sort results by a specific key.
        
        Args:
            key: A key to sort by, either a string attribute name or a callable.
            
        Returns:
            A list of sorted ReportResult objects.
        """
        if isinstance(key, str):
            return sorted(self.results, key=lambda x: getattr(x, key, None))
        else:
            return sorted(self.results, key=key)
    
    def generate_summary_report(self) -> Report:
        """
        Generate a summary report.
        
        Returns:
            A Report object containing a summary of the analysis results.
        """
        # Count results by severity
        severity_counts = {}
        for result in self.results:
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1
        
        # Create summary text
        summary_lines = ["# Analysis Summary"]
        summary_lines.append(f"Total issues found: {len(self.results)}")
        for severity, count in severity_counts.items():
            summary_lines.append(f"- {severity.capitalize()}: {count}")
        
        # Create report
        report = Report(
            title="PR Static Analysis Summary",
            summary="\n".join(summary_lines),
            results=self.results,
            metadata=self.report_metadata.copy()
        )
        
        # Add custom sections
        report.sections = self.custom_sections.copy()
        
        return report
    
    def generate_detailed_report(self) -> Report:
        """
        Generate a detailed report.
        
        Returns:
            A Report object containing detailed analysis results.
        """
        # Create summary text
        summary_lines = ["# Detailed Analysis Report"]
        summary_lines.append(f"Total issues found: {len(self.results)}")
        
        # Group results by file
        files = {}
        for result in self.results:
            if result.file_path:
                if result.file_path not in files:
                    files[result.file_path] = []
                files[result.file_path].append(result)
        
        # Add file sections
        sections = []
        for file_path, file_results in files.items():
            content_lines = [f"## File: {file_path}"]
            for result in file_results:
                content_lines.append(f"- **{result.severity.upper()}**: {result.message}")
                if result.line_number:
                    content_lines.append(f"  - Line: {result.line_number}")
                if result.code_snippet:
                    content_lines.append(f"  - Code: ```\n{result.code_snippet}\n```")
            
            sections.append(ReportSection(
                title=f"File: {file_path}",
                content="\n".join(content_lines),
                order=len(sections)
            ))
        
        # Create report
        report = Report(
            title="PR Static Analysis Detailed Report",
            summary="\n".join(summary_lines),
            results=self.results,
            sections=sections,
            metadata=self.report_metadata.copy()
        )
        
        # Add custom sections
        report.sections.extend(self.custom_sections)
        
        return report
    
    def generate_issue_report(self) -> Report:
        """
        Generate a report focused on issues.
        
        Returns:
            A Report object focused on issues.
        """
        # Create summary text
        summary_lines = ["# Issues Report"]
        summary_lines.append(f"Total issues found: {len(self.results)}")
        
        # Group results by severity
        severities = {}
        for result in self.results:
            if result.severity not in severities:
                severities[result.severity] = []
            severities[result.severity].append(result)
        
        # Add severity sections
        sections = []
        for severity, severity_results in severities.items():
            content_lines = [f"## {severity.capitalize()} Issues"]
            for result in severity_results:
                content_lines.append(f"- **{result.message}**")
                if result.file_path:
                    content_lines.append(f"  - File: {result.file_path}")
                if result.line_number:
                    content_lines.append(f"  - Line: {result.line_number}")
                if result.code_snippet:
                    content_lines.append(f"  - Code: ```\n{result.code_snippet}\n```")
            
            sections.append(ReportSection(
                title=f"{severity.capitalize()} Issues",
                content="\n".join(content_lines),
                order=len(sections)
            ))
        
        # Create report
        report = Report(
            title="PR Static Analysis Issues Report",
            summary="\n".join(summary_lines),
            results=self.results,
            sections=sections,
            metadata=self.report_metadata.copy()
        )
        
        # Add custom sections
        report.sections.extend(self.custom_sections)
        
        return report
    
    def generate_custom_report(self, template: str) -> Report:
        """
        Generate a custom report using a template.
        
        Args:
            template: A template string for the report.
            
        Returns:
            A Report object generated from the template.
        """
        # Simple template substitution
        # In a real implementation, this would use a proper templating engine
        
        # Create a context for template rendering
        context = {
            "results": self.results,
            "metadata": self.report_metadata,
            "options": self.report_options,
            "sections": self.custom_sections,
            "result_count": len(self.results),
        }
        
        # Very basic template substitution
        summary = template
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                summary = summary.replace(f"{{{{{key}}}}}", str(value))
        
        # Create report
        report = Report(
            title=self.report_metadata.get("title", "Custom Analysis Report"),
            summary=summary,
            results=self.results,
            sections=self.custom_sections.copy(),
            metadata=self.report_metadata.copy()
        )
        
        return report
    
    def set_report_options(self, options: Dict[str, Any]) -> None:
        """
        Set options for report generation.
        
        Args:
            options: A dictionary of report options.
        """
        self.report_options.update(options)
    
    def add_custom_section(self, section: ReportSection) -> None:
        """
        Add a custom section to the report.
        
        Args:
            section: A ReportSection object to add.
        """
        self.custom_sections.append(section)
    
    def set_report_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set metadata for the report.
        
        Args:
            metadata: A dictionary of report metadata.
        """
        self.report_metadata.update(metadata)

