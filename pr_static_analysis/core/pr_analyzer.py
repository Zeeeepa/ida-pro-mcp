"""
PR Analyzer Module

This module provides the PRAnalyzer class that orchestrates the PR analysis process.
It implements the main analysis pipeline and hooks for plugins and extensions.
"""
from typing import Dict, List, Any, Optional, Callable, Type
import logging
import os
import tempfile
import shutil
import subprocess
from datetime import datetime

from .analysis_context import PRAnalysisContext, PRData, AnalysisResult
from .rule_engine import RuleEngine
from ..config.config_model import AnalysisConfig

logger = logging.getLogger(__name__)

class AnalysisHook:
    """Base class for analysis hooks."""
    
    def pre_analysis(self, context: PRAnalysisContext) -> None:
        """
        Called before analysis starts.
        
        Args:
            context: The PR analysis context.
        """
        pass
        
    def post_analysis(self, context: PRAnalysisContext, results: List[AnalysisResult]) -> None:
        """
        Called after analysis completes.
        
        Args:
            context: The PR analysis context.
            results: The analysis results.
        """
        pass
        
    def pre_rule(self, context: PRAnalysisContext, rule_id: str) -> None:
        """
        Called before a rule is executed.
        
        Args:
            context: The PR analysis context.
            rule_id: The ID of the rule about to be executed.
        """
        pass
        
    def post_rule(self, context: PRAnalysisContext, rule_id: str, results: List[AnalysisResult]) -> None:
        """
        Called after a rule is executed.
        
        Args:
            context: The PR analysis context.
            rule_id: The ID of the executed rule.
            results: The results of the rule execution.
        """
        pass

class PRAnalyzer:
    """
    Orchestrates the PR analysis process.
    
    This class implements the main analysis pipeline and provides hooks for plugins and extensions.
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize the PR analyzer.
        
        Args:
            config: The analysis configuration.
        """
        self.config = config
        self.rule_engine = RuleEngine(max_workers=config.max_workers)
        self.hooks: List[AnalysisHook] = []
        
    def add_hook(self, hook: AnalysisHook) -> None:
        """
        Add an analysis hook.
        
        Args:
            hook: The hook to add.
        """
        self.hooks.append(hook)
        
    def _run_hooks(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Run a method on all hooks.
        
        Args:
            method_name: The name of the method to run.
            *args: Positional arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.
        """
        for hook in self.hooks:
            method = getattr(hook, method_name)
            try:
                method(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in hook {hook.__class__.__name__}.{method_name}: {e}", exc_info=True)
                
    def _prepare_snapshots(self, pr_data: PRData) -> tuple[str, str]:
        """
        Prepare snapshots of the base and head branches.
        
        Args:
            pr_data: The pull request data.
            
        Returns:
            A tuple of (base_snapshot_path, head_snapshot_path).
        """
        # This is a placeholder implementation. In a real system, this would
        # clone the repository and checkout the appropriate branches.
        base_path = tempfile.mkdtemp(prefix="pr_analysis_base_")
        head_path = tempfile.mkdtemp(prefix="pr_analysis_head_")
        
        # In a real implementation, we would clone the repository and checkout
        # the base and head branches here.
        
        return base_path, head_path
        
    def _cleanup_snapshots(self, base_path: str, head_path: str) -> None:
        """
        Clean up the snapshots.
        
        Args:
            base_path: The path to the base branch snapshot.
            head_path: The path to the head branch snapshot.
        """
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
            
        if os.path.exists(head_path):
            shutil.rmtree(head_path)
            
    def analyze_pr(self, pr_data: PRData) -> List[AnalysisResult]:
        """
        Analyze a pull request.
        
        Args:
            pr_data: The pull request data.
            
        Returns:
            A list of analysis results.
        """
        logger.info(f"Starting analysis of PR {pr_data.pr_id}: {pr_data.title}")
        
        # Create the analysis context
        context = PRAnalysisContext(pr_data)
        
        # Prepare snapshots
        base_path, head_path = self._prepare_snapshots(pr_data)
        context.set_base_snapshot_path(base_path)
        context.set_head_snapshot_path(head_path)
        
        try:
            # Run pre-analysis hooks
            self._run_hooks("pre_analysis", context)
            
            # Load rules
            if self.config.rules_directory:
                self.rule_engine.register_rules_from_directory(
                    self.config.rules_directory,
                    self.config.rules_package_prefix
                )
                
            # Execute rules
            results = self.rule_engine.execute_all_rules(
                context,
                rule_filter=self._create_rule_filter(),
                parallel=self.config.parallel_execution
            )
            
            # Run post-analysis hooks
            self._run_hooks("post_analysis", context, results)
            
            return results
        finally:
            # Clean up snapshots
            if not self.config.keep_snapshots:
                self._cleanup_snapshots(base_path, head_path)
                
    def _create_rule_filter(self) -> Optional[Callable[[str], bool]]:
        """
        Create a rule filter function based on configuration.
        
        Returns:
            A function that takes a rule ID and returns True if the rule should be executed,
            or None if no filtering is needed.
        """
        include_rules = self.config.include_rules
        exclude_rules = self.config.exclude_rules
        include_categories = self.config.include_categories
        exclude_categories = self.config.exclude_categories
        
        if not any([include_rules, exclude_rules, include_categories, exclude_categories]):
            return None
            
        rule_categories = self.rule_engine.get_rule_categories()
        category_to_rules = {category: set(rules) for category, rules in rule_categories.items()}
        rules_by_category = {}
        for category, rules in category_to_rules.items():
            for rule in rules:
                rules_by_category[rule] = category
                
        def rule_filter(rule_id: str) -> bool:
            # If include_rules is specified, only include those rules
            if include_rules and rule_id not in include_rules:
                return False
                
            # If exclude_rules is specified, exclude those rules
            if exclude_rules and rule_id in exclude_rules:
                return False
                
            # Get the category for this rule
            category = rules_by_category.get(rule_id)
            
            # If include_categories is specified, only include rules in those categories
            if include_categories and (not category or category not in include_categories):
                return False
                
            # If exclude_categories is specified, exclude rules in those categories
            if exclude_categories and category and category in exclude_categories:
                return False
                
            return True
            
        return rule_filter

