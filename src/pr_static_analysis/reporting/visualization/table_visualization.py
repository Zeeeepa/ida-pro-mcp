"""
Table visualizations for PR static analysis reports.

This module provides classes for generating table visualizations of analysis results.
"""

from typing import Dict, List, Any, Optional
from .base_visualization import BaseVisualization

class ResultsTable(BaseVisualization):
    """Table of analysis results."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate an HTML table of analysis results.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                columns: List of columns to include
                sort_by: Column to sort by
                sort_desc: Whether to sort in descending order
                
        Returns:
            HTML table
        """
        # Get options
        columns = kwargs.get("columns", ["rule_id", "severity", "category", "message", "file_path", "line"])
        sort_by = kwargs.get("sort_by")
        sort_desc = kwargs.get("sort_desc", False)
        
        # Sort results if requested
        if sort_by:
            results = sorted(results, key=lambda r: r.get(sort_by, ""), reverse=sort_desc)
        
        # Generate the table
        html = """<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
        <tr style="background-color: #f2f2f2;">
"""
        
        # Add column headers
        for column in columns:
            header = column.replace("_", " ").title()
            html += f'            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">{header}</th>\n'
            
        html += """        </tr>
    </thead>
    <tbody>
"""
        
        # Add rows
        for result in results:
            html += '        <tr style="border: 1px solid #ddd;">\n'
            
            for column in columns:
                value = result.get(column, "")
                
                # Format the value based on the column
                if column == "severity":
                    color = self._get_severity_color(value)
                    html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: {color};">{value}</td>\n'
                elif column == "file_path" and "line" in result:
                    html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{value}:{result["line"]}</td>\n'
                else:
                    html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{value}</td>\n'
                    
            html += '        </tr>\n'
            
        html += """    </tbody>
</table>"""
        
        return html
    
    def _get_severity_color(self, severity: str) -> str:
        """
        Get a color for a severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            CSS color
        """
        colors = {
            "critical": "#ffcccc",
            "error": "#ffddcc",
            "warning": "#ffffcc",
            "info": "#ccffff",
            "other": "#f2f2f2"
        }
        
        return colors.get(severity.lower(), "#f2f2f2")

class SummaryTable(BaseVisualization):
    """Summary table of analysis results."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate an HTML summary table of analysis results.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                
        Returns:
            HTML table
        """
        # Count by severity
        severity_counts = {}
        for result in results:
            severity = result.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
        # Count by category
        category_counts = {}
        for result in results:
            category = result.get("category", "other")
            category_counts[category] = category_counts.get(category, 0) + 1
            
        # Generate the table
        html = """<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
        <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Metric</th>
            <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Count</th>
        </tr>
    </thead>
    <tbody>
        <tr style="border: 1px solid #ddd;">
            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;"><strong>Total Issues</strong></td>
            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{}</td>
        </tr>
""".format(len(results))
        
        # Add severity counts
        html += '        <tr style="border: 1px solid #ddd; background-color: #f9f9f9;">\n'
        html += '            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;" colspan="2"><strong>By Severity</strong></td>\n'
        html += '        </tr>\n'
        
        for severity, count in severity_counts.items():
            color = self._get_severity_color(severity)
            html += f'        <tr style="border: 1px solid #ddd;">\n'
            html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd; background-color: {color};">{severity.capitalize()}</td>\n'
            html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{count}</td>\n'
            html += f'        </tr>\n'
            
        # Add category counts
        html += '        <tr style="border: 1px solid #ddd; background-color: #f9f9f9;">\n'
        html += '            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;" colspan="2"><strong>By Category</strong></td>\n'
        html += '        </tr>\n'
        
        for category, count in category_counts.items():
            html += f'        <tr style="border: 1px solid #ddd;">\n'
            html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{category.capitalize()}</td>\n'
            html += f'            <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{count}</td>\n'
            html += f'        </tr>\n'
            
        html += """    </tbody>
</table>"""
        
        return html
    
    def _get_severity_color(self, severity: str) -> str:
        """
        Get a color for a severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            CSS color
        """
        colors = {
            "critical": "#ffcccc",
            "error": "#ffddcc",
            "warning": "#ffffcc",
            "info": "#ccffff",
            "other": "#f2f2f2"
        }
        
        return colors.get(severity.lower(), "#f2f2f2")

