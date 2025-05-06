"""
Visualization components for PR static analysis.

This module provides components for visualizing analysis results.
"""
import base64
import io
from typing import Dict, Any, List, Tuple
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


class ReportVisualizer:
    """Visualizer for analysis reports."""
    
    def generate_summary_chart(self, report: Dict[str, Any]) -> str:
        """Generate a summary chart for a report.
        
        Args:
            report: The report to visualize
            
        Returns:
            Base64 encoded PNG image of the chart
        """
        summary = report['summary']
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Data
        categories = ['Errors', 'Warnings', 'Info']
        values = [summary['error_count'], summary['warning_count'], summary['info_count']]
        colors = ['#f44336', '#ff9800', '#2196f3']
        
        # Create bar chart
        bars = ax.bar(categories, values, color=colors)
        
        # Add labels and title
        ax.set_ylabel('Count')
        ax.set_title('Analysis Results Summary')
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # Convert plot to base64 encoded PNG
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    def generate_severity_distribution(self, report: Dict[str, Any]) -> str:
        """Generate a severity distribution chart for a report.
        
        Args:
            report: The report to visualize
            
        Returns:
            Base64 encoded PNG image of the chart
        """
        summary = report['summary']
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Data
        labels = ['Errors', 'Warnings', 'Info']
        sizes = [summary['error_count'], summary['warning_count'], summary['info_count']]
        colors = ['#f44336', '#ff9800', '#2196f3']
        
        # Remove categories with zero count
        non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
        labels = [labels[i] for i in non_zero_indices]
        sizes = [sizes[i] for i in non_zero_indices]
        colors = [colors[i] for i in non_zero_indices]
        
        # If all counts are zero, return empty chart
        if not sizes:
            plt.text(0.5, 0.5, 'No issues found', horizontalalignment='center',
                     verticalalignment='center', transform=ax.transAxes, fontsize=14)
            plt.axis('off')
        else:
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                shadow=False
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            plt.title('Severity Distribution')
            
            # Make text more readable
            for text in texts:
                text.set_fontsize(12)
            for autotext in autotexts:
                autotext.set_fontsize(12)
                autotext.set_color('white')
        
        # Convert plot to base64 encoded PNG
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    def generate_file_heatmap(self, report: Dict[str, Any]) -> str:
        """Generate a file heatmap for a report.
        
        Args:
            report: The report to visualize
            
        Returns:
            Base64 encoded PNG image of the heatmap
        """
        results = report['results']
        
        # Count issues per file
        file_counts = {}
        for result in results:
            if 'file' in result:
                file_path = result['file']
                severity = result['severity']
                
                if file_path not in file_counts:
                    file_counts[file_path] = {'error': 0, 'warning': 0, 'info': 0}
                
                file_counts[file_path][severity] += 1
        
        # If no files with issues, return empty chart
        if not file_counts:
            fig, ax = plt.subplots(figsize=(10, 6))
            plt.text(0.5, 0.5, 'No file issues found', horizontalalignment='center',
                     verticalalignment='center', transform=ax.transAxes, fontsize=14)
            plt.axis('off')
        else:
            # Sort files by total issue count
            sorted_files = sorted(
                file_counts.items(),
                key=lambda x: sum(x[1].values()),
                reverse=True
            )
            
            # Limit to top 10 files for readability
            if len(sorted_files) > 10:
                sorted_files = sorted_files[:10]
            
            # Prepare data for stacked bar chart
            files = [self._shorten_path(f[0]) for f in sorted_files]
            error_counts = [f[1]['error'] for f in sorted_files]
            warning_counts = [f[1]['warning'] for f in sorted_files]
            info_counts = [f[1]['info'] for f in sorted_files]
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create stacked bar chart
            bar_width = 0.6
            y_pos = np.arange(len(files))
            
            ax.barh(y_pos, error_counts, bar_width, color='#f44336', label='Errors')
            ax.barh(y_pos, warning_counts, bar_width, left=error_counts, color='#ff9800', label='Warnings')
            ax.barh(y_pos, info_counts, bar_width, 
                   left=[e + w for e, w in zip(error_counts, warning_counts)], 
                   color='#2196f3', label='Info')
            
            # Add labels and title
            ax.set_yticks(y_pos)
            ax.set_yticklabels(files)
            ax.invert_yaxis()  # Labels read top-to-bottom
            ax.set_xlabel('Number of Issues')
            ax.set_title('Issues by File')
            ax.legend()
            
            # Adjust layout to make room for long filenames
            plt.tight_layout()
        
        # Convert plot to base64 encoded PNG
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _shorten_path(self, path: str, max_length: int = 40) -> str:
        """Shorten a file path for display purposes.
        
        Args:
            path: The file path to shorten
            max_length: Maximum length of the shortened path
            
        Returns:
            Shortened path
        """
        if len(path) <= max_length:
            return path
            
        # Split path into components
        parts = path.split('/')
        
        # If only filename is longer than max_length, truncate it
        if len(parts) == 1:
            return path[:max_length-3] + '...'
            
        # Keep the first and last parts, shorten the middle
        first = parts[0]
        last = '/'.join(parts[-2:])  # Keep last directory and filename
        
        # Calculate how much space we have for the middle
        middle_length = max_length - len(first) - len(last) - 5  # 5 for '/.../'
        
        if middle_length <= 0:
            # Not enough space, just show the filename
            return '...' + parts[-1]
            
        return f"{first}/.../{last}"

