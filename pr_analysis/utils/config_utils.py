"""
Configuration utilities for PR static analysis.

This module provides utilities for loading and saving configuration.
"""

import json
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class Config:
    """Configuration for the PR static analysis system."""
    
    # General settings
    enabled_rules: List[str] = field(default_factory=list)
    disabled_rules: List[str] = field(default_factory=list)
    custom_rule_paths: List[str] = field(default_factory=list)
    output_format: str = "json"
    output_directory: str = "reports"
    
    # GitHub settings
    github_token: Optional[str] = None
    github_api_url: str = "https://api.github.com"
    
    # Analysis settings
    max_files_per_analysis: int = 100
    max_lines_per_file: int = 10000
    ignore_generated_files: bool = True
    ignore_binary_files: bool = True
    ignore_deleted_files: bool = False
    
    # Rule settings
    rule_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default rule settings."""
        # Set default rule settings if not provided
        if not self.rule_settings:
            self.rule_settings = {
                "code_integrity": {
                    "max_file_size": 1000000,  # 1MB
                    "max_line_length": 120,
                },
                "parameter": {
                    "check_types": True,
                    "check_defaults": True,
                },
                "implementation": {
                    "check_complexity": True,
                    "max_complexity": 15,
                },
            }
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: The default value to return if the key is not found
            
        Returns:
            The configuration value
        """
        if hasattr(self, key):
            return getattr(self, key)
        
        # Check if the key is in rule_settings
        parts = key.split(".")
        if len(parts) > 1:
            current = self.rule_settings
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    return default
            return current
            
        return default
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        if hasattr(self, key):
            setattr(self, key, value)
            return
            
        # Check if the key is in rule_settings
        parts = key.split(".")
        if len(parts) > 1:
            current = self.rule_settings
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            A dictionary representation of the configuration
        """
        return {
            "enabled_rules": self.enabled_rules,
            "disabled_rules": self.disabled_rules,
            "custom_rule_paths": self.custom_rule_paths,
            "output_format": self.output_format,
            "output_directory": self.output_directory,
            "github_token": self.github_token,
            "github_api_url": self.github_api_url,
            "max_files_per_analysis": self.max_files_per_analysis,
            "max_lines_per_file": self.max_lines_per_file,
            "ignore_generated_files": self.ignore_generated_files,
            "ignore_binary_files": self.ignore_binary_files,
            "ignore_deleted_files": self.ignore_deleted_files,
            "rule_settings": self.rule_settings,
        }


def load_config(config_path: str) -> Config:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        A Config object
    """
    if not os.path.exists(config_path):
        return Config()
        
    with open(config_path, "r") as f:
        if config_path.endswith(".json"):
            config_dict = json.load(f)
        elif config_path.endswith((".yaml", ".yml")):
            config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path}")
            
    config = Config()
    for key, value in config_dict.items():
        config.set(key, value)
        
    return config


def save_config(config: Config, config_path: str) -> None:
    """
    Save configuration to a file.
    
    Args:
        config: The configuration to save
        config_path: Path to the configuration file
    """
    config_dict = config.to_dict()
    
    with open(config_path, "w") as f:
        if config_path.endswith(".json"):
            json.dump(config_dict, f, indent=2)
        elif config_path.endswith((".yaml", ".yml")):
            yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path}")


def find_config_file(start_dir: str = ".") -> Optional[str]:
    """
    Find a configuration file in the current directory or parent directories.
    
    Args:
        start_dir: The directory to start searching from
        
    Returns:
        The path to the configuration file, or None if not found
    """
    current_dir = os.path.abspath(start_dir)
    
    while current_dir != os.path.dirname(current_dir):  # Stop at root directory
        for filename in [".pr-analysis.json", ".pr-analysis.yaml", ".pr-analysis.yml"]:
            config_path = os.path.join(current_dir, filename)
            if os.path.exists(config_path):
                return config_path
                
        current_dir = os.path.dirname(current_dir)
        
    return None

