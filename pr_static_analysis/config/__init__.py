"""
Config Module

This module contains configuration handling for the PR static analysis system.
"""
from .config_model import AnalysisConfig
from .default_config import get_default_config, load_config, merge_configs

__all__ = [
    "AnalysisConfig",
    "get_default_config",
    "load_config",
    "merge_configs"
]

