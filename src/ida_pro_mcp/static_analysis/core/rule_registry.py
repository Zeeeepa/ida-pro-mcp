"""
Registry for analysis rules.

This module provides a registry for all analysis rules in the system,
making it easy to discover and use rules.
"""
from typing import Dict, List, Type, Optional

from .base_rule import BaseRule


class RuleRegistry:
    """
    Registry for analysis rules.
    
    This class provides a central registry for all analysis rules in the system,
    making it easy to discover and use rules.
    """
    def __init__(self):
        """Initialize the rule registry."""
        self._rules: Dict[str, Type[BaseRule]] = {}
    
    def register(self, rule_class: Type[BaseRule]) -> None:
        """
        Register a rule class.
        
        Args:
            rule_class: The rule class to register
        """
        # Create an instance to get the name
        rule = rule_class()
        self._rules[rule.name] = rule_class
    
    def get_rule(self, name: str) -> Optional[Type[BaseRule]]:
        """
        Get a rule class by name.
        
        Args:
            name: Name of the rule to get
            
        Returns:
            The rule class, or None if not found
        """
        return self._rules.get(name)
    
    def get_all_rules(self) -> List[Type[BaseRule]]:
        """
        Get all registered rule classes.
        
        Returns:
            List of all registered rule classes
        """
        return list(self._rules.values())
    
    def get_rules_by_category(self, category: str) -> List[Type[BaseRule]]:
        """
        Get all rule classes in a category.
        
        Args:
            category: Category of rules to get (e.g., 'code_integrity', 'parameter_validation')
            
        Returns:
            List of rule classes in the category
        """
        return [rule_class for rule_class in self._rules.values() 
                if rule_class.__module__.endswith(category)]


# Global rule registry instance
rule_registry = RuleRegistry()


def register_rule(rule_class: Type[BaseRule]) -> Type[BaseRule]:
    """
    Decorator to register a rule class.
    
    Args:
        rule_class: The rule class to register
        
    Returns:
        The rule class (unchanged)
    """
    rule_registry.register(rule_class)
    return rule_class

