"""
Base rule for PR static analysis.

This module provides the BaseRule class that all analysis rules inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Set, ClassVar, Optional

from ..core.analysis_context import PRAnalysisContext, AnalysisResult


class BaseRule(ABC):
    """
    Base class for all analysis rules.
    
    All rules must inherit from this class and implement the analyze method.
    """
    
    # Class variables that can be overridden by subclasses
    RULE_ID: ClassVar[str] = "base_rule"
    RULE_NAME: ClassVar[str] = "Base Rule"
    RULE_DESCRIPTION: ClassVar[str] = "Base rule that all rules inherit from"
    RULE_CATEGORY: ClassVar[str] = "base"
    RULE_PRIORITY: ClassVar[int] = 0  # Higher values = higher priority
    RULE_DEPENDENCIES: ClassVar[List[str]] = []
    
    @classmethod
    def get_rule_id(cls) -> str:
        """
        Get the ID of the rule.
        
        Returns:
            The rule ID
        """
        return cls.RULE_ID
        
    @classmethod
    def get_rule_name(cls) -> str:
        """
        Get the name of the rule.
        
        Returns:
            The rule name
        """
        return cls.RULE_NAME
        
    @classmethod
    def get_description(cls) -> str:
        """
        Get the description of the rule.
        
        Returns:
            The rule description
        """
        return cls.RULE_DESCRIPTION
        
    @classmethod
    def get_category(cls) -> str:
        """
        Get the category of the rule.
        
        Returns:
            The rule category
        """
        return cls.RULE_CATEGORY
        
    @classmethod
    def get_priority(cls) -> int:
        """
        Get the priority of the rule.
        
        Returns:
            The rule priority
        """
        return cls.RULE_PRIORITY
        
    @classmethod
    def get_dependencies(cls) -> List[str]:
        """
        Get the dependencies of the rule.
        
        Returns:
            A list of rule IDs that this rule depends on
        """
        return cls.RULE_DEPENDENCIES
        
    @abstractmethod
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR and return results.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        pass

