"""
Static analysis system for PR validation.

This package contains components for analyzing pull requests and identifying
potential issues in the code.
"""

from .pr_analyzer import PRAnalyzer
from .core import BaseRule, AnalysisResult, AnalysisContext, RuleEngine, rule_registry, register_rule

__all__ = [
    "PRAnalyzer",
    "BaseRule",
    "AnalysisResult",
    "AnalysisContext",
    "RuleEngine",
    "rule_registry",
    "register_rule",
]

