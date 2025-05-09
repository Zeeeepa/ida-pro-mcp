"""
Base Rule Module

This module provides the BaseRule class that all analysis rules must inherit from.
"""
from typing import List, ClassVar, Dict, Any
from abc import ABC, abstractmethod

from ..core.analysis_context import PRAnalysisContext, AnalysisResult

class BaseRule(ABC):
    """
    Base class for all analysis rules.
    
    All rules must inherit from this class and implement the analyze method.
    """
    
    # Class variables to be overridden by subclasses
    RULE_ID: ClassVar[str] = "base_rule"
    CATEGORY: ClassVar[str] = "uncategorized"
    DESCRIPTION: ClassVar[str] = "Base rule class"
    SEVERITY: ClassVar[str] = "info"  # One of: "info", "warning", "error"
    
    @classmethod
    def get_rule_id(cls) -> str:
        """
        Get the rule ID.
        
        Returns:
            The rule ID.
        """
        return cls.RULE_ID
        
    @classmethod
    def get_category(cls) -> str:
        """
        Get the rule category.
        
        Returns:
            The rule category.
        """
        return cls.CATEGORY
        
    @classmethod
    def get_description(cls) -> str:
        """
        Get the rule description.
        
        Returns:
            The rule description.
        """
        return cls.DESCRIPTION
        
    @classmethod
    def get_severity(cls) -> str:
        """
        Get the rule severity.
        
        Returns:
            The rule severity.
        """
        return cls.SEVERITY
        
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Get the rule metadata.
        
        Returns:
            A dictionary containing rule metadata.
        """
        return {
            "id": cls.get_rule_id(),
            "category": cls.get_category(),
            "description": cls.get_description(),
            "severity": cls.get_severity()
        }
        
    @abstractmethod
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze the PR and return results.
        
        Args:
            context: The PR analysis context.
            
        Returns:
            A list of analysis results.
        """
        pass

