"""
Visualization for PR static analysis.

This module provides visualization tools for analysis results.
"""

from typing import Dict, List, Any, Optional
import json
import os


class Visualization:
    """
    Visualization for analysis results.
    
    This class provides methods for generating visualizations of analysis results.
    """
    
    def __init__(self):
        """Initialize a new visualization."""
        pass
        
    def generate_html_chart(self, data: Dict[str, Any]) -> str:
        """
        Generate an HTML chart from data.
        
        Args:
            data: The data to visualize
            
        Returns:
            An HTML string with the chart
        """
        # Extract summary data
        summary = data.get("summary", {})
        errors = summary.get("errors", 0)
        warnings = summary.get("warnings", 0)
        infos = summary.get("infos", 0)
        
        issues_by_rule = summary.get("issues_by_rule", {})
        issues_by_file = summary.get("issues_by_file", {})
        
        # Generate HTML with Chart.js
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PR Analysis Visualization</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #555; margin-top: 20px; }
                .chart-container { width: 600px; height: 400px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>PR Analysis Visualization</h1>
            
            <h2>Issues by Severity</h2>
            <div class="chart-container">
                <canvas id="severityChart"></canvas>
            </div>
            
            <h2>Issues by Rule</h2>
            <div class="chart-container">
                <canvas id="ruleChart"></canvas>
            </div>
            
            <h2>Issues by File</h2>
            <div class="chart-container">
                <canvas id="fileChart"></canvas>
            </div>
            
            <script>
                // Severity chart
                const severityCtx = document.getElementById('severityChart').getContext('2d');
                const severityChart = new Chart(severityCtx, {
                    type: 'pie',
                    data: {
                        labels: ['Errors', 'Warnings', 'Info'],
                        datasets: [{
                            data: [%d, %d, %d],
                            backgroundColor: ['#d9534f', '#f0ad4e', '#5bc0de'],
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Issues by Severity'
                            }
                        }
                    }
                });
                
                // Rule chart
                const ruleCtx = document.getElementById('ruleChart').getContext('2d');
                const ruleChart = new Chart(ruleCtx, {
                    type: 'bar',
                    data: {
                        labels: %s,
                        datasets: [{
                            label: 'Issues',
                            data: %s,
                            backgroundColor: '#5bc0de',
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Issues by Rule'
                            }
                        }
                    }
                });
                
                // File chart
                const fileCtx = document.getElementById('fileChart').getContext('2d');
                const fileChart = new Chart(fileCtx, {
                    type: 'bar',
                    data: {
                        labels: %s,
                        datasets: [{
                            label: 'Issues',
                            data: %s,
                            backgroundColor: '#5bc0de',
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Issues by File'
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
        """ % (
            errors, warnings, infos,
            json.dumps(list(issues_by_rule.keys())),
            json.dumps(list(issues_by_rule.values())),
            json.dumps(list(issues_by_file.keys())),
            json.dumps(list(issues_by_file.values())),
        )
        
        return html
        
    def save_html_chart(self, data: Dict[str, Any], filename: str) -> str:
        """
        Generate and save an HTML chart.
        
        Args:
            data: The data to visualize
            filename: The filename to save to
            
        Returns:
            The path to the saved chart
        """
        html = self.generate_html_chart(data)
        
        with open(filename, "w") as f:
            f.write(html)
            
        return filename
        
    def generate_visualization(self, data: Dict[str, Any], 
                             output_format: str = "html",
                             output_file: Optional[str] = None) -> str:
        """
        Generate a visualization.
        
        Args:
            data: The data to visualize
            output_format: The format of the visualization ("html")
            output_file: Optional file to save the visualization to
            
        Returns:
            The visualization as a string or the path to the saved visualization
        """
        if output_format == "html":
            html = self.generate_html_chart(data)
            
            if output_file:
                with open(output_file, "w") as f:
                    f.write(html)
                return output_file
            else:
                return html
        else:
            raise ValueError(f"Unsupported visualization format: {output_format}")

