"""
Chart visualizations for PR static analysis reports.

This module provides classes for generating chart visualizations of analysis results.
"""

from typing import Dict, List, Any, Optional
import io
import matplotlib.pyplot as plt
from .base_visualization import BaseVisualization

class SeverityPieChart(BaseVisualization):
    """Pie chart of results by severity."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a pie chart of results by severity.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                title: Chart title
                figsize: Figure size as (width, height) tuple
                
        Returns:
            Base64-encoded image data
        """
        # Get options
        title = kwargs.get("title", "Results by Severity")
        figsize = kwargs.get("figsize", (8, 8))
        
        # Count results by severity
        severity_counts = {}
        for result in results:
            severity = result.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
        # Create the pie chart
        labels = list(severity_counts.keys())
        sizes = list(severity_counts.values())
        
        plt.figure(figsize=figsize)
        plt.pie(sizes, labels=labels, autopct="%1.1f%%")
        plt.axis("equal")
        plt.title(title)
        
        # Save the chart to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        
        # Encode the image
        img_data = self.encode_image(buf.read())
        plt.close()
        
        return img_data

class CategoryBarChart(BaseVisualization):
    """Bar chart of results by category."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a bar chart of results by category.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                title: Chart title
                figsize: Figure size as (width, height) tuple
                
        Returns:
            Base64-encoded image data
        """
        # Get options
        title = kwargs.get("title", "Results by Category")
        figsize = kwargs.get("figsize", (10, 6))
        
        # Count results by category
        category_counts = {}
        for result in results:
            category = result.get("category", "other")
            category_counts[category] = category_counts.get(category, 0) + 1
            
        # Create the bar chart
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        
        plt.figure(figsize=figsize)
        plt.bar(categories, counts)
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the chart to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        
        # Encode the image
        img_data = self.encode_image(buf.read())
        plt.close()
        
        return img_data

class SeverityBarChart(BaseVisualization):
    """Bar chart of results by severity."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a bar chart of results by severity.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                title: Chart title
                figsize: Figure size as (width, height) tuple
                
        Returns:
            Base64-encoded image data
        """
        # Get options
        title = kwargs.get("title", "Results by Severity")
        figsize = kwargs.get("figsize", (10, 6))
        
        # Count results by severity
        severity_counts = {}
        for result in results:
            severity = result.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
        # Create the bar chart
        severities = list(severity_counts.keys())
        counts = list(severity_counts.values())
        
        plt.figure(figsize=figsize)
        plt.bar(severities, counts)
        plt.xlabel("Severity")
        plt.ylabel("Count")
        plt.title(title)
        plt.tight_layout()
        
        # Save the chart to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        
        # Encode the image
        img_data = self.encode_image(buf.read())
        plt.close()
        
        return img_data

