"""
Graph visualizations for PR static analysis reports.

This module provides classes for generating graph visualizations of analysis results.
"""

from typing import Dict, List, Any, Optional
import io
import matplotlib.pyplot as plt
import networkx as nx
from .base_visualization import BaseVisualization

class FileHeatmap(BaseVisualization):
    """Heatmap of results by file."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a heatmap of results by file.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                title: Chart title
                figsize: Figure size as (width, height) tuple
                max_files: Maximum number of files to show
                
        Returns:
            Base64-encoded image data
        """
        # Get options
        title = kwargs.get("title", "Top Files by Issue Count")
        figsize = kwargs.get("figsize", (10, 6))
        max_files = kwargs.get("max_files", 10)
        
        # Count results by file
        file_counts = {}
        for result in results:
            file_path = result.get("file_path", "unknown")
            file_counts[file_path] = file_counts.get(file_path, 0) + 1
            
        # Sort files by count
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        files = [f[0] for f in sorted_files[:max_files]]  # Top N files
        counts = [f[1] for f in sorted_files[:max_files]]
        
        plt.figure(figsize=figsize)
        plt.barh(files, counts)
        plt.xlabel("Count")
        plt.ylabel("File")
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

class DependencyGraph(BaseVisualization):
    """Graph of file dependencies."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a graph of file dependencies.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                title: Chart title
                figsize: Figure size as (width, height) tuple
                dependencies: Dictionary mapping files to their dependencies
                
        Returns:
            Base64-encoded image data
        """
        # Get options
        title = kwargs.get("title", "File Dependencies")
        figsize = kwargs.get("figsize", (12, 8))
        dependencies = kwargs.get("dependencies", {})
        
        # If no dependencies provided, try to extract from results
        if not dependencies:
            dependencies = {}
            for result in results:
                if "dependencies" in result:
                    file_path = result.get("file_path", "unknown")
                    dependencies[file_path] = result["dependencies"]
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for file, deps in dependencies.items():
            G.add_node(file)
            for dep in deps:
                G.add_edge(file, dep)
        
        # Draw the graph
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color="lightblue", 
                node_size=1500, edge_color="gray", arrows=True, 
                font_size=8, font_weight="bold")
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

class IssueGraph(BaseVisualization):
    """Graph of issues and their relationships."""
    
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a graph of issues and their relationships.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
                title: Chart title
                figsize: Figure size as (width, height) tuple
                
        Returns:
            Base64-encoded image data
        """
        # Get options
        title = kwargs.get("title", "Issue Relationships")
        figsize = kwargs.get("figsize", (12, 8))
        
        # Create a graph
        G = nx.Graph()
        
        # Add nodes for each issue
        for i, result in enumerate(results):
            rule_id = result.get("rule_id", f"issue_{i}")
            severity = result.get("severity", "info")
            G.add_node(rule_id, severity=severity)
        
        # Add edges between issues in the same file
        file_issues = {}
        for result in results:
            file_path = result.get("file_path")
            if file_path:
                if file_path not in file_issues:
                    file_issues[file_path] = []
                file_issues[file_path].append(result.get("rule_id"))
        
        for file_path, issues in file_issues.items():
            for i in range(len(issues)):
                for j in range(i+1, len(issues)):
                    G.add_edge(issues[i], issues[j], file=file_path)
        
        # Draw the graph
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G)
        
        # Color nodes by severity
        severity_colors = {
            "critical": "red",
            "error": "orange",
            "warning": "yellow",
            "info": "blue",
            "other": "gray"
        }
        
        node_colors = [severity_colors.get(G.nodes[node].get("severity", "other"), "gray") for node in G.nodes]
        
        nx.draw(G, pos, with_labels=True, node_color=node_colors, 
                node_size=1000, edge_color="gray", 
                font_size=8, font_weight="bold")
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

