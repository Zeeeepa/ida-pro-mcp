"""
Base Formatter Module

This module provides the base formatter interface for report formatters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseFormatter(ABC):
    """
    Base class for report formatters.
    
    This abstract class defines the interface for report formatters.
    All formatters should inherit from this class and implement the format method.
    """
    
    @abstractmethod
    def format(
        self, 
        analysis_results: Dict[str, Any], 
        visualizations: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Format analysis results into a report.
        
        Args:
            analysis_results: Analysis results to format
            visualizations: Optional dictionary of visualization data
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            The formatted report as a string
        """
        pass

