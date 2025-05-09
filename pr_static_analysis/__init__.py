"""
PR Static Analysis System

A system for static analysis of pull requests.
"""
import logging
from typing import List, Dict, Any, Optional

from .core.analysis_context import PRAnalysisContext, PRData, AnalysisResult
from .core.rule_engine import RuleEngine
from .core.pr_analyzer import PRAnalyzer, AnalysisHook
from .rules.base_rule import BaseRule
from .config.config_model import AnalysisConfig
from .config.default_config import get_default_config, load_config, merge_configs

__version__ = "0.1.0"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

__all__ = [
    "PRAnalysisContext",
    "PRData",
    "AnalysisResult",
    "RuleEngine",
    "PRAnalyzer",
    "AnalysisHook",
    "BaseRule",
    "AnalysisConfig",
    "get_default_config",
    "load_config",
    "merge_configs",
    "__version__"
]

