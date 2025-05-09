"""
PR analyzer for the static analysis system.

This module provides the PRAnalyzer class, which is responsible for analyzing
pull requests using the rule engine.
"""
from typing import List, Dict, Any, Optional

from .core import AnalysisContext, AnalysisResult, RuleEngine


class PRAnalyzer:
    """
    Analyzer for pull requests.
    
    This class is responsible for analyzing pull requests using the rule engine.
    """
    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        """
        Initialize the PR analyzer.
        
        Args:
            rule_engine: Rule engine to use, or None to create a new one
        """
        self.rule_engine = rule_engine or RuleEngine()
    
    def analyze_pr(self, pr_data: Dict[str, Any]) -> List[AnalysisResult]:
        """
        Analyze a pull request.
        
        Args:
            pr_data: Data about the PR to analyze
            
        Returns:
            List of analysis results
        """
        # Create analysis context
        context = AnalysisContext(pr_data)
        
        # Run rules
        return self.rule_engine.run_rules(context)
    
    def analyze_pr_by_category(self, pr_data: Dict[str, Any], category: str) -> List[AnalysisResult]:
        """
        Analyze a pull request using rules in a specific category.
        
        Args:
            pr_data: Data about the PR to analyze
            category: Category of rules to run (e.g., 'code_integrity', 'parameter_validation')
            
        Returns:
            List of analysis results
        """
        # Create analysis context
        context = AnalysisContext(pr_data)
        
        # Run rules in category
        return self.rule_engine.run_rules_by_category(category, context)
    
    def analyze_pr_by_rule(self, pr_data: Dict[str, Any], rule_name: str) -> List[AnalysisResult]:
        """
        Analyze a pull request using a specific rule.
        
        Args:
            pr_data: Data about the PR to analyze
            rule_name: Name of the rule to run
            
        Returns:
            List of analysis results
        """
        # Create analysis context
        context = AnalysisContext(pr_data)
        
        # Run specific rule
        return self.rule_engine.run_rule_by_name(rule_name, context)

