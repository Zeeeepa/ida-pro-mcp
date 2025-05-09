"""
Base visualization for PR static analysis reports.

This module provides the BaseVisualization class that all visualizations should inherit from.
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import io
import base64

class BaseVisualization(ABC):
    """
    Base class for visualizations.
    
    This class provides methods for generating visualizations of analysis results.
    """
    
    @abstractmethod
    def generate(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a visualization.
        
        Args:
            results: Analysis results
            **kwargs: Additional visualization options
            
        Returns:
            Visualization data (e.g., base64-encoded image, HTML, etc.)
        """
        pass
    
    def encode_image(self, image_data: bytes) -> str:
        """
        Encode image data as base64.
        
        Args:
            image_data: Raw image data
            
        Returns:
            Base64-encoded image data
        """
        return base64.b64encode(image_data).decode("utf-8")
        
    def get_image_html(self, image_data: str, alt: str = "Visualization", 
                      width: Optional[int] = None, height: Optional[int] = None) -> str:
        """
        Get HTML for displaying an image.
        
        Args:
            image_data: Base64-encoded image data
            alt: Alt text for the image
            width: Image width
            height: Image height
            
        Returns:
            HTML for displaying the image
        """
        style = ""
        if width:
            style += f"width:{width}px;"
        if height:
            style += f"height:{height}px;"
            
        return f'<img src="data:image/png;base64,{image_data}" alt="{alt}" style="{style}">'
        
    def get_markdown_image(self, image_data: str, alt: str = "Visualization") -> str:
        """
        Get Markdown for displaying an image.
        
        Args:
            image_data: Base64-encoded image data
            alt: Alt text for the image
            
        Returns:
            Markdown for displaying the image
        """
        return f"![{alt}](data:image/png;base64,{image_data})"

