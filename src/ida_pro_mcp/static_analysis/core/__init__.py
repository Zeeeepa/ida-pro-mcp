"""
Core components for the static analysis system.

This package contains the base classes and interfaces used by the static
analysis system.
"""

from .base_rule import BaseRule, AnalysisResult, AnalysisContext
from .rule_registry import rule_registry, register_rule
from .rule_engine import RuleEngine

__all__ = [
    "BaseRule", 
    "AnalysisResult", 
    "AnalysisContext",
    "rule_registry",
    "register_rule",
    "RuleEngine",
]

