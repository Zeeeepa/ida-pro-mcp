"""
Chart Visualization Module

This module provides a visualization for generating charts from analysis results.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from .base_visualization import BaseVisualization

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import io
    import base64
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartVisualization(BaseVisualization):
    """
    Visualization for generating charts from analysis results.
    
    This visualization can generate various types of charts (bar, line, pie, etc.)
    from analysis results using matplotlib.
    """
    
    def __init__(
        self,
        chart_type: str = 'bar',
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6),
        dpi: int = 100,
        format: str = 'png'
    ):
        """
        Initialize a new ChartVisualization.
        
        Args:
            chart_type: Type of chart to generate ('bar', 'line', 'pie', 'scatter', etc.)
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size (width, height) in inches
            dpi: Figure resolution in dots per inch
            format: Image format ('png', 'jpg', 'svg', etc.)
            
        Raises:
            ImportError: If matplotlib is not installed
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "Matplotlib is required for ChartVisualization. "
                "Install it with: pip install matplotlib"
            )
        
        self.chart_type = chart_type
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.figsize = figsize
        self.dpi = dpi
        self.format = format
        
    def generate(
        self, 
        analysis_results: Dict[str, Any], 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chart visualization from analysis results.
        
        Args:
            analysis_results: Analysis results to visualize
            **kwargs: Additional visualization-specific arguments, including:
                - data_key: Key in analysis_results containing the data to visualize
                - x_key: Key for x-axis values
                - y_key: Key for y-axis values
                - labels: Labels for the data points
                - colors: Colors for the data points
                - chart_type: Override the default chart type
                - title: Override the default chart title
                - xlabel: Override the default x-axis label
                - ylabel: Override the default y-axis label
                - figsize: Override the default figure size
                - dpi: Override the default figure resolution
                - format: Override the default image format
                - as_html: Whether to return the chart as an HTML img tag
                - as_base64: Whether to return the chart as a base64-encoded string
                - save_path: Path to save the chart to
            
        Returns:
            A dictionary containing the visualization data, including:
                - image: The chart image as a base64-encoded string
                - html: The chart as an HTML img tag (if as_html is True)
                - format: The image format
                - chart_type: The chart type
                - title: The chart title
        """
        try:
            # Get chart parameters
            data_key = kwargs.get('data_key')
            x_key = kwargs.get('x_key')
            y_key = kwargs.get('y_key')
            labels = kwargs.get('labels')
            colors = kwargs.get('colors')
            chart_type = kwargs.get('chart_type', self.chart_type)
            title = kwargs.get('title', self.title)
            xlabel = kwargs.get('xlabel', self.xlabel)
            ylabel = kwargs.get('ylabel', self.ylabel)
            figsize = kwargs.get('figsize', self.figsize)
            dpi = kwargs.get('dpi', self.dpi)
            format = kwargs.get('format', self.format)
            as_html = kwargs.get('as_html', True)
            as_base64 = kwargs.get('as_base64', True)
            save_path = kwargs.get('save_path')
            
            # Extract the data to visualize
            data = self._extract_data(analysis_results, data_key, x_key, y_key)
            
            if not data:
                logging.warning("No data to visualize")
                return {
                    'error': "No data to visualize",
                    'chart_type': chart_type,
                    'title': title
                }
            
            # Create the figure and axis
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            
            # Generate the chart based on the chart type
            if chart_type == 'bar':
                self._generate_bar_chart(ax, data, labels, colors)
            elif chart_type == 'line':
                self._generate_line_chart(ax, data, labels, colors)
            elif chart_type == 'pie':
                self._generate_pie_chart(ax, data, labels, colors)
            elif chart_type == 'scatter':
                self._generate_scatter_chart(ax, data, labels, colors)
            else:
                logging.warning(f"Unsupported chart type: {chart_type}")
                return {
                    'error': f"Unsupported chart type: {chart_type}",
                    'chart_type': chart_type,
                    'title': title
                }
            
            # Set chart title and labels
            if title:
                ax.set_title(title)
            
            if xlabel:
                ax.set_xlabel(xlabel)
            
            if ylabel:
                ax.set_ylabel(ylabel)
            
            # Save the chart to a file if requested
            if save_path:
                plt.savefig(save_path, format=format, dpi=dpi)
            
            # Convert the chart to a base64-encoded string
            if as_base64 or as_html:
                buf = io.BytesIO()
                plt.savefig(buf, format=format, dpi=dpi)
                buf.seek(0)
                img_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
                
                result = {
                    'image': img_data,
                    'format': format,
                    'chart_type': chart_type,
                    'title': title
                }
                
                if as_html:
                    result['html'] = f'<img src="data:image/{format};base64,{img_data}" alt="{title or "Chart"}" />'
                
                return result
            else:
                plt.close(fig)
                return {
                    'chart_type': chart_type,
                    'title': title,
                    'format': format
                }
        
        except Exception as e:
            logging.error(f"Error generating chart visualization: {e}")
            return {
                'error': str(e),
                'chart_type': self.chart_type,
                'title': self.title
            }
    
    def _extract_data(
        self, 
        analysis_results: Dict[str, Any], 
        data_key: Optional[str] = None,
        x_key: Optional[str] = None,
        y_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data from analysis results for visualization.
        
        Args:
            analysis_results: Analysis results to extract data from
            data_key: Key in analysis_results containing the data to visualize
            x_key: Key for x-axis values
            y_key: Key for y-axis values
            
        Returns:
            A dictionary containing the extracted data
        """
        if data_key and data_key in analysis_results:
            # Use the specified data key
            data = analysis_results[data_key]
        elif 'metrics' in analysis_results:
            # Use metrics data
            data = analysis_results['metrics']
        else:
            # Try to find suitable data
            for key in ['files_added', 'files_modified', 'files_removed', 'issues']:
                if key in analysis_results and analysis_results[key]:
                    if isinstance(analysis_results[key], dict):
                        data = analysis_results[key]
                        break
                    elif isinstance(analysis_results[key], list) and len(analysis_results[key]) > 0:
                        # Convert list to dict if possible
                        if all(isinstance(item, dict) for item in analysis_results[key]):
                            # Group by a common key if available
                            if x_key and y_key and all(x_key in item and y_key in item for item in analysis_results[key]):
                                data = {item[x_key]: item[y_key] for item in analysis_results[key]}
                                break
                        
                        # Count occurrences of items
                        data = {}
                        for item in analysis_results[key]:
                            if isinstance(item, dict) and 'severity' in item:
                                # Group by severity for issues
                                severity = item['severity']
                                data[severity] = data.get(severity, 0) + 1
                            elif isinstance(item, str):
                                # Count by file extension for files
                                ext = item.split('.')[-1] if '.' in item else 'other'
                                data[ext] = data.get(ext, 0) + 1
                        break
            else:
                # No suitable data found
                return {}
        
        # Extract x and y values if specified
        if x_key and y_key and isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return {item[x_key]: item[y_key] for item in data if x_key in item and y_key in item}
        
        return data
    
    def _generate_bar_chart(
        self, 
        ax, 
        data: Dict[str, Any], 
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None
    ) -> None:
        """
        Generate a bar chart.
        
        Args:
            ax: Matplotlib axis
            data: Data to visualize
            labels: Labels for the data points
            colors: Colors for the data points
        """
        if isinstance(data, dict):
            # Use dictionary keys and values
            x = list(data.keys())
            y = list(data.values())
        elif isinstance(data, list) and all(isinstance(item, (int, float)) for item in data):
            # Use list indices and values
            x = list(range(len(data)))
            y = data
        else:
            # Unsupported data format
            raise ValueError("Unsupported data format for bar chart")
        
        # Use provided labels if available
        if labels and len(labels) == len(x):
            x = labels
        
        # Create the bar chart
        bars = ax.bar(x, y, color=colors)
        
        # Add value labels on top of the bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, str(height),
                    ha='center', va='bottom')
    
    def _generate_line_chart(
        self, 
        ax, 
        data: Dict[str, Any], 
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None
    ) -> None:
        """
        Generate a line chart.
        
        Args:
            ax: Matplotlib axis
            data: Data to visualize
            labels: Labels for the data points
            colors: Colors for the data points
        """
        if isinstance(data, dict):
            # Use dictionary keys and values
            x = list(data.keys())
            y = list(data.values())
        elif isinstance(data, list) and all(isinstance(item, (int, float)) for item in data):
            # Use list indices and values
            x = list(range(len(data)))
            y = data
        else:
            # Unsupported data format
            raise ValueError("Unsupported data format for line chart")
        
        # Use provided labels if available
        if labels and len(labels) == len(x):
            x = labels
        
        # Create the line chart
        ax.plot(x, y, marker='o', color=colors[0] if colors else None)
    
    def _generate_pie_chart(
        self, 
        ax, 
        data: Dict[str, Any], 
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None
    ) -> None:
        """
        Generate a pie chart.
        
        Args:
            ax: Matplotlib axis
            data: Data to visualize
            labels: Labels for the data points
            colors: Colors for the data points
        """
        if isinstance(data, dict):
            # Use dictionary keys and values
            labels = list(data.keys())
            values = list(data.values())
        elif isinstance(data, list) and all(isinstance(item, (int, float)) for item in data):
            # Use list values
            values = data
            labels = [f"Item {i+1}" for i in range(len(data))]
        else:
            # Unsupported data format
            raise ValueError("Unsupported data format for pie chart")
        
        # Create the pie chart
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    def _generate_scatter_chart(
        self, 
        ax, 
        data: Dict[str, Any], 
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None
    ) -> None:
        """
        Generate a scatter chart.
        
        Args:
            ax: Matplotlib axis
            data: Data to visualize
            labels: Labels for the data points
            colors: Colors for the data points
        """
        if isinstance(data, dict):
            # Use dictionary keys and values
            x = list(data.keys())
            y = list(data.values())
        elif isinstance(data, list) and all(isinstance(item, tuple) and len(item) == 2 for item in data):
            # Use list of (x, y) tuples
            x = [item[0] for item in data]
            y = [item[1] for item in data]
        else:
            # Unsupported data format
            raise ValueError("Unsupported data format for scatter chart")
        
        # Create the scatter chart
        ax.scatter(x, y, color=colors[0] if colors else None)
        
        # Add labels if provided
        if labels and len(labels) == len(x):
            for i, label in enumerate(labels):
                ax.annotate(label, (x[i], y[i]))

