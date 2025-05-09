"""
Rule engine for the PR static analysis system.

This module provides the RuleEngine class, which is responsible for running
rules and collecting results.
"""
from typing import List, Dict, Any, Optional, Type, Set

from .base_rule import BaseRule, AnalysisResult, AnalysisContext
from .rule_registry import rule_registry


class RuleEngine:
    """
    Engine for running analysis rules.
    
    This class is responsible for running rules and collecting results.
    """
    def __init__(self, rules: Optional[List[BaseRule]] = None):
        """
        Initialize the rule engine.
        
        Args:
            rules: List of rule instances to run, or None to use all registered rules
        """
        self.rules = rules or [rule_cls() for rule_cls in rule_registry.get_all_rules()]
    
    def run_rules(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run all rules and collect results.
        
        Args:
            context: Analysis context containing PR data and other information
            
        Returns:
            List of analysis results from all rules
        """
        results = []
        
        for rule in self.rules:
            if rule.should_run(context):
                rule_results = rule.run(context)
                results.extend(rule_results)
        
        return results
    
    def run_rule_by_name(self, rule_name: str, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run a specific rule by name and collect results.
        
        Args:
            rule_name: Name of the rule to run
            context: Analysis context containing PR data and other information
            
        Returns:
            List of analysis results from the rule, or empty list if rule not found
        """
        for rule in self.rules:
            if rule.name == rule_name and rule.should_run(context):
                return rule.run(context)
        
        return []
    
    def run_rules_by_category(self, category: str, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run all rules in a category and collect results.
        
        Args:
            category: Category of rules to run (e.g., 'code_integrity', 'parameter_validation')
            context: Analysis context containing PR data and other information
            
        Returns:
            List of analysis results from all rules in the category
        """
        results = []
        
        for rule in self.rules:
            if rule.__class__.__module__.endswith(category) and rule.should_run(context):
                rule_results = rule.run(context)
                results.extend(rule_results)
        
        return results

