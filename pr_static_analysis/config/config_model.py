"""
Configuration Model Module

This module provides the configuration models for the PR static analysis system.
"""
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import os
import json
import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuration for PR analysis."""
    
    # Rule execution settings
    max_workers: int = 4
    parallel_execution: bool = True
    
    # Rule filtering
    include_rules: Set[str] = field(default_factory=set)
    exclude_rules: Set[str] = field(default_factory=set)
    include_categories: Set[str] = field(default_factory=set)
    exclude_categories: Set[str] = field(default_factory=set)
    
    # Rule loading
    rules_directory: Optional[str] = None
    rules_package_prefix: str = ""
    
    # Snapshot settings
    keep_snapshots: bool = False
    
    # Output settings
    output_format: str = "json"  # One of: "json", "yaml", "text"
    output_file: Optional[str] = None
    
    # Reporting settings
    report_all_results: bool = False  # If False, only report failures
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AnalysisConfig':
        """
        Create a configuration from a dictionary.
        
        Args:
            config_dict: The configuration dictionary.
            
        Returns:
            An AnalysisConfig instance.
        """
        # Convert list fields to sets
        for field_name in ['include_rules', 'exclude_rules', 'include_categories', 'exclude_categories']:
            if field_name in config_dict and isinstance(config_dict[field_name], list):
                config_dict[field_name] = set(config_dict[field_name])
                
        # Extract known fields
        known_fields = {
            k: v for k, v in config_dict.items() 
            if k in [f.name for f in fields(cls)]
        }
        
        # Extract custom settings (all other fields)
        custom_settings = {
            k: v for k, v in config_dict.items()
            if k not in known_fields
        }
        
        if custom_settings:
            known_fields['custom_settings'] = custom_settings
            
        return cls(**known_fields)
        
    @classmethod
    def from_file(cls, file_path: str) -> 'AnalysisConfig':
        """
        Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file (JSON or YAML).
            
        Returns:
            An AnalysisConfig instance.
            
        Raises:
            ValueError: If the file format is not supported or the file cannot be parsed.
        """
        if not os.path.exists(file_path):
            raise ValueError(f"Configuration file does not exist: {file_path}")
            
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                config_dict = json.load(f)
            elif file_path.endswith(('.yaml', '.yml')):
                config_dict = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_path}")
                
        return cls.from_dict(config_dict)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            A dictionary representation of the configuration.
        """
        result = {}
        
        for field_name, field_value in self.__dict__.items():
            # Convert sets to lists for serialization
            if isinstance(field_value, set):
                result[field_name] = list(field_value)
            else:
                result[field_name] = field_value
                
        return result
        
    def save_to_file(self, file_path: str) -> None:
        """
        Save the configuration to a file.
        
        Args:
            file_path: Path to the output file.
            
        Raises:
            ValueError: If the file format is not supported.
        """
        config_dict = self.to_dict()
        
        with open(file_path, 'w') as f:
            if file_path.endswith('.json'):
                json.dump(config_dict, f, indent=2)
            elif file_path.endswith(('.yaml', '.yml')):
                yaml.dump(config_dict, f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_path}")
                
def fields(cls):
    """Get the fields of a dataclass."""
    return cls.__dataclass_fields__.items()

