"""
Configuration utilities for PR static analysis reports.

This module provides classes for configuring reports.
"""

from typing import Dict, List, Any, Optional

class ReportConfig:
    """
    Configuration for reports.
    
    This class provides methods for configuring reports.
    """
    
    def __init__(self):
        """Initialize the report configuration."""
        self.config = {}
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
        
    def remove(self, key: str) -> None:
        """
        Remove a configuration value.
        
        Args:
            key: Configuration key
        """
        if key in self.config:
            del self.config[key]
            
    def clear(self) -> None:
        """Clear all configuration values."""
        self.config.clear()
        
    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration with values from a dictionary.
        
        Args:
            config: Dictionary of configuration values
        """
        self.config.update(config)
        
    def as_dict(self) -> Dict[str, Any]:
        """
        Get the configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()

