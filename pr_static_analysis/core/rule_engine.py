"""
Rule Engine Module

This module provides the RuleEngine class for managing and executing analysis rules.
It implements the rule registry system and methods for rule execution and result aggregation.
"""
from typing import Dict, List, Type, Any, Optional, Callable
import logging
import importlib
import inspect
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..rules.base_rule import BaseRule
from .analysis_context import PRAnalysisContext, AnalysisResult

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Manages and executes analysis rules.
    
    This class provides methods for registering rules, executing them, and aggregating results.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the rule engine.
        
        Args:
            max_workers: The maximum number of worker threads for parallel rule execution.
        """
        self._rules: Dict[str, Type[BaseRule]] = {}
        self._max_workers = max_workers
        
    def register_rule(self, rule_class: Type[BaseRule]) -> None:
        """
        Register a rule class.
        
        Args:
            rule_class: The rule class to register.
            
        Raises:
            ValueError: If the rule ID is already registered.
        """
        if not issubclass(rule_class, BaseRule):
            raise ValueError(f"Rule class must be a subclass of BaseRule: {rule_class.__name__}")
            
        rule_id = rule_class.get_rule_id()
        if rule_id in self._rules:
            raise ValueError(f"Rule ID already registered: {rule_id}")
            
        self._rules[rule_id] = rule_class
        logger.debug(f"Registered rule: {rule_id}")
        
    def register_rules_from_module(self, module_name: str) -> int:
        """
        Register all rules from a module.
        
        Args:
            module_name: The name of the module to import.
            
        Returns:
            The number of rules registered.
        """
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            return 0
            
        count = 0
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseRule) and 
                obj != BaseRule):
                try:
                    self.register_rule(obj)
                    count += 1
                except ValueError as e:
                    logger.warning(f"Failed to register rule {name}: {e}")
                    
        logger.info(f"Registered {count} rules from module {module_name}")
        return count
        
    def register_rules_from_directory(self, directory: str, package_prefix: str = "") -> int:
        """
        Register all rules from Python files in a directory.
        
        Args:
            directory: The directory to scan for rule modules.
            package_prefix: The package prefix to use for importing modules.
            
        Returns:
            The number of rules registered.
        """
        if not os.path.isdir(directory):
            logger.error(f"Directory does not exist: {directory}")
            return 0
            
        count = 0
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove .py extension
                full_module_name = f"{package_prefix}.{module_name}" if package_prefix else module_name
                count += self.register_rules_from_module(full_module_name)
                
        return count
        
    def get_rule(self, rule_id: str) -> Optional[Type[BaseRule]]:
        """
        Get a rule class by ID.
        
        Args:
            rule_id: The ID of the rule to get.
            
        Returns:
            The rule class, or None if not found.
        """
        return self._rules.get(rule_id)
        
    def get_all_rules(self) -> Dict[str, Type[BaseRule]]:
        """
        Get all registered rules.
        
        Returns:
            A dictionary mapping rule IDs to rule classes.
        """
        return self._rules.copy()
        
    def execute_rule(self, rule_id: str, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Execute a single rule.
        
        Args:
            rule_id: The ID of the rule to execute.
            context: The PR analysis context.
            
        Returns:
            A list of analysis results.
            
        Raises:
            ValueError: If the rule ID is not registered.
        """
        rule_class = self.get_rule(rule_id)
        if not rule_class:
            raise ValueError(f"Rule not registered: {rule_id}")
            
        context.start_rule(rule_id)
        rule = rule_class()
        
        try:
            results = rule.analyze(context)
        except Exception as e:
            logger.error(f"Error executing rule {rule_id}: {e}", exc_info=True)
            error_result = AnalysisResult(
                rule_id=rule_id,
                status="error",
                message=f"Rule execution failed: {str(e)}",
                details={"exception": str(e)}
            )
            results = [error_result]
            
        context.complete_rule(rule_id)
        return results
        
    def execute_all_rules(self, context: PRAnalysisContext, 
                          rule_filter: Optional[Callable[[str], bool]] = None,
                          parallel: bool = True) -> List[AnalysisResult]:
        """
        Execute all registered rules.
        
        Args:
            context: The PR analysis context.
            rule_filter: Optional function to filter which rules to execute.
            parallel: Whether to execute rules in parallel.
            
        Returns:
            A list of all analysis results.
        """
        rule_ids = list(self._rules.keys())
        if rule_filter:
            rule_ids = [rule_id for rule_id in rule_ids if rule_filter(rule_id)]
            
        context.start_analysis(len(rule_ids))
        all_results = []
        
        if parallel and len(rule_ids) > 1:
            with ThreadPoolExecutor(max_workers=min(self._max_workers, len(rule_ids))) as executor:
                future_to_rule = {
                    executor.submit(self.execute_rule, rule_id, context): rule_id
                    for rule_id in rule_ids
                }
                
                for future in as_completed(future_to_rule):
                    rule_id = future_to_rule[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                    except Exception as e:
                        logger.error(f"Error executing rule {rule_id}: {e}", exc_info=True)
        else:
            for rule_id in rule_ids:
                results = self.execute_rule(rule_id, context)
                all_results.extend(results)
                
        context.complete_analysis()
        return all_results
        
    def get_rule_categories(self) -> Dict[str, List[str]]:
        """
        Get rule IDs grouped by category.
        
        Returns:
            A dictionary mapping categories to lists of rule IDs.
        """
        categories: Dict[str, List[str]] = {}
        
        for rule_id, rule_class in self._rules.items():
            category = rule_class.get_category()
            if category not in categories:
                categories[category] = []
            categories[category].append(rule_id)
            
        return categories

