"""
Rules Module

This module contains the rules for PR static analysis.
"""
from .base_rule import BaseRule
from .example_rule import FileExtensionRule, LineCountRule

__all__ = [
    "BaseRule",
    "FileExtensionRule",
    "LineCountRule"
]

