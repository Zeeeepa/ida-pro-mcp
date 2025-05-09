"""
Configuration module for PR static analysis reporting.

This module provides configuration functionality for the reporting system.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ReportingConfig:
    """Configuration for the reporting system."""
    
    DEFAULT_CONFIG = {
        "default_format": "markdown",
        "include_visualizations": True,
        "delivery": {
            "github_pr_comment": {
                "enabled": True
            },
            "file_system": {
                "enabled": True,
                "output_dir": "reports"
            },
            "email": {
                "enabled": False,
                "smtp": {
                    "server": "smtp.example.com",
                    "port": 587,
                    "use_tls": True,
                    "username": "",
                    "password": "",
                    "sender": "pr-analysis@example.com"
                },
                "recipients": []
            }
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Merge user config with default config
            self._merge_config(self.config, user_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Recursively merge source config into target config.
        
        Args:
            target: Target configuration dict
            source: Source configuration dict
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        parts = key.split('.')
        current = self.config
        
        for part in parts:
            if part not in current:
                return default
            current = current[part]
        
        return current
    
    def set(self, key: str, value: Any):
        """Set a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Configuration value
        """
        parts = key.split('.')
        current = self.config
        
        # Navigate to the parent of the key
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
    
    def save(self, config_path: str):
        """Save configuration to a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration.
        
        Returns:
            Configuration dict
        """
        return self.config.copy()

