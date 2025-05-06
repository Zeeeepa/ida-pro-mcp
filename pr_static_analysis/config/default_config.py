"""
Default Configuration Module

This module provides the default configuration for the PR static analysis system.
"""
from typing import Dict, Any
import os
import logging

from .config_model import AnalysisConfig

logger = logging.getLogger(__name__)

def get_default_config() -> AnalysisConfig:
    """
    Get the default configuration.
    
    Returns:
        The default AnalysisConfig instance.
    """
    return AnalysisConfig(
        max_workers=4,
        parallel_execution=True,
        rules_directory=os.path.join(os.path.dirname(__file__), "..", "rules"),
        rules_package_prefix="pr_static_analysis.rules",
        output_format="json",
        report_all_results=False
    )
    
def load_config(config_path: str = None) -> AnalysisConfig:
    """
    Load configuration from a file or use the default configuration.
    
    Args:
        config_path: Path to the configuration file. If None, the default configuration is used.
        
    Returns:
        An AnalysisConfig instance.
    """
    if not config_path:
        logger.info("No configuration file specified, using default configuration")
        return get_default_config()
        
    try:
        logger.info(f"Loading configuration from {config_path}")
        return AnalysisConfig.from_file(config_path)
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        logger.warning("Using default configuration")
        return get_default_config()
        
def merge_configs(base_config: AnalysisConfig, override_config: Dict[str, Any]) -> AnalysisConfig:
    """
    Merge a base configuration with override values.
    
    Args:
        base_config: The base configuration.
        override_config: Dictionary with override values.
        
    Returns:
        A new AnalysisConfig instance with merged values.
    """
    config_dict = base_config.to_dict()
    
    # Update with override values
    for key, value in override_config.items():
        if key in config_dict:
            # Special handling for set fields
            if isinstance(config_dict[key], list) and isinstance(value, list):
                config_dict[key] = list(set(config_dict[key] + value))
            else:
                config_dict[key] = value
        else:
            # Add to custom settings
            if 'custom_settings' not in config_dict:
                config_dict['custom_settings'] = {}
            config_dict['custom_settings'][key] = value
            
    return AnalysisConfig.from_dict(config_dict)

