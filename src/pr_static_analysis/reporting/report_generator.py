"""
Report Generator Module

This module provides the main ReportGenerator class that orchestrates the process
of generating and delivering reports for PR static analysis results.
"""

from typing import Any, Dict, List, Optional, Type, Union

from .formatters.base_formatter import BaseFormatter
from .delivery.base_delivery import BaseDelivery
from .visualization.base_visualization import BaseVisualization


class ReportGenerator:
    """
    Main class for generating and delivering reports for PR static analysis results.
    
    This class orchestrates the process of formatting analysis results into reports
    and delivering them through various channels.
    
    Attributes:
        formatters (Dict[str, BaseFormatter]): Dictionary of registered formatters
        delivery_channels (Dict[str, BaseDelivery]): Dictionary of registered delivery channels
        visualizations (Dict[str, BaseVisualization]): Dictionary of registered visualizations
    """
    
    def __init__(self):
        """Initialize a new ReportGenerator."""
        self.formatters = {}
        self.delivery_channels = {}
        self.visualizations = {}
        
    def register_formatter(self, name: str, formatter: BaseFormatter) -> None:
        """
        Register a formatter with the report generator.
        
        Args:
            name: Name of the formatter
            formatter: Formatter instance
        """
        self.formatters[name] = formatter
        
    def register_delivery_channel(self, name: str, delivery_channel: BaseDelivery) -> None:
        """
        Register a delivery channel with the report generator.
        
        Args:
            name: Name of the delivery channel
            delivery_channel: Delivery channel instance
        """
        self.delivery_channels[name] = delivery_channel
        
    def register_visualization(self, name: str, visualization: BaseVisualization) -> None:
        """
        Register a visualization with the report generator.
        
        Args:
            name: Name of the visualization
            visualization: Visualization instance
        """
        self.visualizations[name] = visualization
        
    def generate_report(
        self, 
        analysis_results: Dict[str, Any], 
        format_name: str, 
        visualization_names: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a report from analysis results.
        
        Args:
            analysis_results: Analysis results to format
            format_name: Name of the formatter to use
            visualization_names: Optional list of visualization names to include
            **kwargs: Additional arguments to pass to the formatter
            
        Returns:
            The formatted report
            
        Raises:
            ValueError: If the specified formatter is not registered
        """
        if format_name not in self.formatters:
            raise ValueError(f"Formatter '{format_name}' not registered")
            
        formatter = self.formatters[format_name]
        
        # Generate visualizations if requested
        visualizations = {}
        if visualization_names:
            for viz_name in visualization_names:
                if viz_name in self.visualizations:
                    visualizations[viz_name] = self.visualizations[viz_name].generate(analysis_results)
        
        # Generate the report
        return formatter.format(analysis_results, visualizations=visualizations, **kwargs)
    
    def deliver_report(
        self, 
        report: str, 
        delivery_channel_name: str, 
        **kwargs
    ) -> bool:
        """
        Deliver a report through a specified channel.
        
        Args:
            report: The report to deliver
            delivery_channel_name: Name of the delivery channel to use
            **kwargs: Additional arguments to pass to the delivery channel
            
        Returns:
            True if delivery was successful, False otherwise
            
        Raises:
            ValueError: If the specified delivery channel is not registered
        """
        if delivery_channel_name not in self.delivery_channels:
            raise ValueError(f"Delivery channel '{delivery_channel_name}' not registered")
            
        delivery_channel = self.delivery_channels[delivery_channel_name]
        return delivery_channel.deliver(report, **kwargs)
    
    def generate_and_deliver_report(
        self, 
        analysis_results: Dict[str, Any], 
        format_name: str, 
        delivery_channel_name: str,
        visualization_names: Optional[List[str]] = None,
        formatter_kwargs: Optional[Dict[str, Any]] = None,
        delivery_kwargs: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Generate and deliver a report in a single operation.
        
        Args:
            analysis_results: Analysis results to format
            format_name: Name of the formatter to use
            delivery_channel_name: Name of the delivery channel to use
            visualization_names: Optional list of visualization names to include
            formatter_kwargs: Additional arguments to pass to the formatter
            delivery_kwargs: Additional arguments to pass to the delivery channel
            
        Returns:
            True if delivery was successful, False otherwise
            
        Raises:
            ValueError: If the specified formatter or delivery channel is not registered
        """
        formatter_kwargs = formatter_kwargs or {}
        delivery_kwargs = delivery_kwargs or {}
        
        report = self.generate_report(
            analysis_results, 
            format_name, 
            visualization_names=visualization_names,
            **formatter_kwargs
        )
        
        return self.deliver_report(
            report, 
            delivery_channel_name, 
            **delivery_kwargs
        )

