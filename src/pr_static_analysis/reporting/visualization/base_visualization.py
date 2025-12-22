"""
Base Visualization Module

This module provides the base visualization interface for report visualizations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseVisualization(ABC):
    """
    Base class for report visualizations.
    
    This abstract class defines the interface for report visualizations.
    All visualizations should inherit from this class and implement the generate method.
    """
    
    @abstractmethod
    def generate(
        self, 
        analysis_results: Dict[str, Any], 
        **kwargs
    ) -> Any:
        """
        Generate a visualization from analysis results.
        
        Args:
            analysis_results: Analysis results to visualize
            **kwargs: Additional visualization-specific arguments
            
        Returns:
            The generated visualization (format depends on the specific visualization)
        """
        pass

