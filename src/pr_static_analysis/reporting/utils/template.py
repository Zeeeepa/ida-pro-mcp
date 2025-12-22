"""
Template utilities for PR static analysis reports.

This module provides classes for creating custom report templates.
"""

from typing import Dict, List, Any, Optional
import jinja2

class ReportTemplate:
    """
    Template for customizing reports.
    
    This class provides methods for creating custom report templates.
    """
    
    def __init__(self, template_str: str):
        """
        Initialize the report template.
        
        Args:
            template_str: Template string
        """
        self.template_str = template_str
        self.env = jinja2.Environment(autoescape=True)
        self.template = self.env.from_string(template_str)
        
    def render(self, context: Dict[str, Any]) -> str:
        """
        Render the template with the given context.
        
        Args:
            context: Template context
            
        Returns:
            Rendered template
        """
        return self.template.render(**context)

class ReportSection:
    """
    Section of a report.
    
    This class represents a section of a report that can be customized.
    """
    
    def __init__(self, title: str, content: str = "", template: Optional[ReportTemplate] = None):
        """
        Initialize the report section.
        
        Args:
            title: Section title
            content: Section content
            template: Section template
        """
        self.title = title
        self.content = content
        self.template = template
        
    def render(self, context: Dict[str, Any] = None) -> str:
        """
        Render the section.
        
        Args:
            context: Template context
            
        Returns:
            Rendered section
        """
        if self.template and context:
            return self.template.render(context)
        return self.content

class ReportCustomizer:
    """
    Customizer for reports.
    
    This class provides methods for customizing reports.
    """
    
    def __init__(self):
        """Initialize the report customizer."""
        self.sections = []
        
    def add_section(self, section: ReportSection) -> None:
        """
        Add a section to the report.
        
        Args:
            section: Report section
        """
        self.sections.append(section)
        
    def remove_section(self, title: str) -> None:
        """
        Remove a section from the report.
        
        Args:
            title: Section title
        """
        self.sections = [s for s in self.sections if s.title != title]
        
    def get_section(self, title: str) -> Optional[ReportSection]:
        """
        Get a section by title.
        
        Args:
            title: Section title
            
        Returns:
            Report section or None if not found
        """
        for section in self.sections:
            if section.title == title:
                return section
        return None
        
    def render(self, context: Dict[str, Any] = None) -> str:
        """
        Render the customized report.
        
        Args:
            context: Template context
            
        Returns:
            Rendered report
        """
        report = ""
        for section in self.sections:
            report += section.render(context) + "\n\n"
        return report

