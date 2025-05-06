"""
Rule engine for PR static analysis.

This module provides the RuleEngine class for managing and executing analysis rules.
"""

import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Optional, Set, Type, Any, Callable
import time

from ..rules.base_rule import BaseRule
from .analysis_context import PRAnalysisContext, AnalysisResult

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Engine for managing and executing analysis rules.
    
    This class provides methods for rule registration, execution, and result aggregation.
    """
    
    def __init__(self):
        """Initialize a new rule engine."""
        self.rules: Dict[str, Type[BaseRule]] = {}
        self.rule_categories: Dict[str, Set[str]] = {}
        self.rule_dependencies: Dict[str, Set[str]] = {}
        self.rule_priorities: Dict[str, int] = {}
        
    def register_rule(self, rule_class: Type[BaseRule]) -> None:
        """
        Register a rule with the engine.
        
        Args:
            rule_class: The rule class to register
        """
        rule_id = rule_class.get_rule_id()
        if rule_id in self.rules:
            logger.warning(f"Rule with ID {rule_id} already registered, overwriting")
            
        self.rules[rule_id] = rule_class
        
        # Register rule category
        category = rule_class.get_category()
        if category not in self.rule_categories:
            self.rule_categories[category] = set()
        self.rule_categories[category].add(rule_id)
        
        # Register rule dependencies
        dependencies = rule_class.get_dependencies()
        if dependencies:
            self.rule_dependencies[rule_id] = set(dependencies)
            
        # Register rule priority
        self.rule_priorities[rule_id] = rule_class.get_priority()
        
    def register_rules_from_module(self, module_name: str) -> None:
        """
        Register all rules from a module.
        
        Args:
            module_name: The name of the module to register rules from
        """
        try:
            module = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseRule) and 
                    obj != BaseRule):
                    self.register_rule(obj)
        except ImportError:
            logger.error(f"Failed to import module {module_name}")
            
    def discover_and_register_rules(self, package_name: str = "pr_analysis.rules") -> None:
        """
        Discover and register all rules in a package.
        
        Args:
            package_name: The name of the package to discover rules in
        """
        try:
            package = importlib.import_module(package_name)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if not is_pkg:
                    self.register_rules_from_module(name)
        except ImportError:
            logger.error(f"Failed to import package {package_name}")
            
    def get_rules_by_category(self, category: str) -> List[Type[BaseRule]]:
        """
        Get all rules in a category.
        
        Args:
            category: The category to get rules for
            
        Returns:
            A list of rule classes in the specified category
        """
        rule_ids = self.rule_categories.get(category, set())
        return [self.rules[rule_id] for rule_id in rule_ids if rule_id in self.rules]
        
    def get_rule_execution_order(self) -> List[str]:
        """
        Get the order in which rules should be executed.
        
        This method takes into account rule dependencies and priorities.
        
        Returns:
            A list of rule IDs in the order they should be executed
        """
        # Start with all rules
        remaining_rules = set(self.rules.keys())
        execution_order = []
        
        while remaining_rules:
            # Find rules that can be executed (all dependencies satisfied)
            executable_rules = []
            for rule_id in remaining_rules:
                dependencies = self.rule_dependencies.get(rule_id, set())
                if all(dep in execution_order for dep in dependencies):
                    executable_rules.append(rule_id)
                    
            if not executable_rules:
                # Circular dependency detected
                logger.warning("Circular dependency detected in rules")
                # Add all remaining rules to break the cycle
                execution_order.extend(sorted(remaining_rules))
                break
                
            # Sort executable rules by priority (higher priority first)
            executable_rules.sort(key=lambda r: self.rule_priorities.get(r, 0), reverse=True)
            
            # Add the highest priority rule to the execution order
            next_rule = executable_rules[0]
            execution_order.append(next_rule)
            remaining_rules.remove(next_rule)
            
        return execution_order
        
    def execute_rule(self, rule_id: str, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Execute a single rule.
        
        Args:
            rule_id: The ID of the rule to execute
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        if rule_id not in self.rules:
            logger.warning(f"Rule with ID {rule_id} not found")
            return []
            
        rule_class = self.rules[rule_id]
        rule = rule_class()
        
        try:
            start_time = time.time()
            results = rule.analyze(context)
            end_time = time.time()
            
            # Add execution time to metadata
            for result in results:
                if "execution_time" not in result.metadata:
                    result.metadata["execution_time"] = end_time - start_time
                    
            context.mark_rule_processed(rule_id)
            return results
        except Exception as e:
            logger.error(f"Error executing rule {rule_id}: {e}")
            context.mark_rule_failed(rule_id)
            return []
            
    def execute_rules(self, context: PRAnalysisContext, 
                      rule_filter: Optional[Callable[[str], bool]] = None) -> List[AnalysisResult]:
        """
        Execute all rules.
        
        Args:
            context: The analysis context
            rule_filter: Optional function to filter which rules to execute
            
        Returns:
            A list of analysis results
        """
        context.start_analysis()
        
        execution_order = self.get_rule_execution_order()
        if rule_filter:
            execution_order = [r for r in execution_order if rule_filter(r)]
            
        # Update metadata with total rules
        context.metadata["total_rules"] = len(execution_order)
        
        all_results = []
        for rule_id in execution_order:
            results = self.execute_rule(rule_id, context)
            all_results.extend(results)
            
            # Add results to context
            for result in results:
                context.add_result(result)
                
        context.complete_analysis()
        return all_results
        
    def execute_rules_by_category(self, context: PRAnalysisContext, 
                                 category: str) -> List[AnalysisResult]:
        """
        Execute all rules in a category.
        
        Args:
            context: The analysis context
            category: The category of rules to execute
            
        Returns:
            A list of analysis results
        """
        rule_ids = self.rule_categories.get(category, set())
        return self.execute_rules(context, lambda r: r in rule_ids)
        
    def get_rule_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the registered rules.
        
        Returns:
            A dictionary with rule statistics
        """
        return {
            "total_rules": len(self.rules),
            "categories": {
                category: len(rules) 
                for category, rules in self.rule_categories.items()
            },
            "rules_with_dependencies": len(self.rule_dependencies),
        }

