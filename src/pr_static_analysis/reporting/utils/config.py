"""
Configuration Utilities

This module provides utilities for loading and saving configuration files.
"""

import json
import logging
import os
import yaml
from typing import Any, Dict, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load a configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        The loaded configuration as a dictionary
        
    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an unsupported format
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    _, ext = os.path.splitext(config_path)
    ext = ext.lower()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if ext == '.json':
                return json.load(f)
            elif ext in ('.yaml', '.yml'):
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")
    except Exception as e:
        logging.error(f"Error loading configuration file: {e}")
        raise


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save a configuration to a file.
    
    Args:
        config: Configuration to save
        config_path: Path to save the configuration to
        
    Raises:
        ValueError: If the configuration file has an unsupported format
    """
    _, ext = os.path.splitext(config_path)
    ext = ext.lower()
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            if ext == '.json':
                json.dump(config, f, indent=2)
            elif ext in ('.yaml', '.yml'):
                yaml.dump(config, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")
    except Exception as e:
        logging.error(f"Error saving configuration file: {e}")
        raise

