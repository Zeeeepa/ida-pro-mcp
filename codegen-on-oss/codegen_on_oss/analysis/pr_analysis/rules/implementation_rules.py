"""
Implementation rules for PR static analysis.

This module defines rules for validating implementation correctness, including
adherence to design patterns, coding standards, best practices, and logic flow.
"""

import ast
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from codegen_on_oss.analysis.pr_analysis.rules.base_rule import (
    BaseRule,
    RuleCategory,
    RuleResult,
    RuleSeverity,
)


class DesignPatternRule(BaseRule):
    """Rule for checking adherence to design patterns."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the design pattern rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="design_pattern",
            name="Design Pattern",
            description="Checks adherence to design patterns",
            category=RuleCategory.IMPLEMENTATION,
            severity=RuleSeverity.WARNING,
            config=config,
        )
        
        # Default configuration
        self.patterns = self.config.get("patterns", ["singleton", "factory", "observer"])

    def apply(self, context: Any) -> List[RuleResult]:
        """
        Apply the rule to the analysis context.

        Args:
            context: The analysis context containing the data to analyze.

        Returns:
            A list of rule results.
        """
        self.clear_results()
        
        # Get changed files from the context
        changed_files = context.get_changed_files()
        
        for file_path in changed_files:
            # Skip non-Python files
            if not file_path.endswith(".py"):
                continue
                
            # Get file content
            file_content = context.get_file_content(file_path, context.head_ref)
            
            try:
                # Parse the file
                tree = ast.parse(file_content)
                
                # Check for design patterns
                if "singleton" in self.patterns:
                    self._check_singleton_pattern(tree, file_path)
                
                if "factory" in self.patterns:
                    self._check_factory_pattern(tree, file_path)
                
                if "observer" in self.patterns:
                    self._check_observer_pattern(tree, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_singleton_pattern(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for proper implementation of the Singleton pattern.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class name suggests it's a singleton
                if "singleton" in node.name.lower():
                    # Check for instance variable
                    has_instance_var = False
                    has_instance_method = False
                    
                    for item in node.body:
                        # Check for class variable named _instance or similar
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and "_instance" in target.id.lower():
                                    has_instance_var = True
                        
                        # Check for getInstance or similar method
                        if isinstance(item, ast.FunctionDef) and "instance" in item.name.lower():
                            has_instance_method = True
                    
                    if not has_instance_var or not has_instance_method:
                        self.create_result(
                            message=f"Class '{node.name}' appears to be a Singleton but doesn't follow the pattern correctly",
                            file_path=file_path,
                            line_number=node.lineno,
                        )
    
    def _check_factory_pattern(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for proper implementation of the Factory pattern.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class name suggests it's a factory
                if "factory" in node.name.lower():
                    # Check for create/get/make methods
                    has_factory_method = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if any(keyword in item.name.lower() for keyword in ["create", "get", "make"]):
                                has_factory_method = True
                                break
                    
                    if not has_factory_method:
                        self.create_result(
                            message=f"Class '{node.name}' appears to be a Factory but doesn't have create/get/make methods",
                            file_path=file_path,
                            line_number=node.lineno,
                        )
    
    def _check_observer_pattern(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for proper implementation of the Observer pattern.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class name suggests it's an observer or subject
                is_observer = "observer" in node.name.lower()
                is_subject = "subject" in node.name.lower() or "observable" in node.name.lower()
                
                if is_observer:
                    # Check for update method
                    has_update_method = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and "update" in item.name.lower():
                            has_update_method = True
                            break
                    
                    if not has_update_method:
                        self.create_result(
                            message=f"Class '{node.name}' appears to be an Observer but doesn't have an update method",
                            file_path=file_path,
                            line_number=node.lineno,
                        )
                
                if is_subject:
                    # Check for register/add/attach and notify methods
                    has_register_method = False
                    has_notify_method = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if any(keyword in item.name.lower() for keyword in ["register", "add", "attach"]):
                                has_register_method = True
                            if "notify" in item.name.lower():
                                has_notify_method = True
                    
                    if not has_register_method or not has_notify_method:
                        self.create_result(
                            message=f"Class '{node.name}' appears to be a Subject but doesn't have register and notify methods",
                            file_path=file_path,
                            line_number=node.lineno,
                        )


class CodingStandardRule(BaseRule):
    """Rule for checking adherence to coding standards."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the coding standard rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="coding_standard",
            name="Coding Standard",
            description="Checks adherence to coding standards",
            category=RuleCategory.IMPLEMENTATION,
            severity=RuleSeverity.WARNING,
            config=config,
        )
        
        # Default configuration
        self.max_line_length = self.config.get("max_line_length", 100)
        self.check_docstrings = self.config.get("check_docstrings", True)
        self.check_naming = self.config.get("check_naming", True)

    def apply(self, context: Any) -> List[RuleResult]:
        """
        Apply the rule to the analysis context.

        Args:
            context: The analysis context containing the data to analyze.

        Returns:
            A list of rule results.
        """
        self.clear_results()
        
        # Get changed files from the context
        changed_files = context.get_changed_files()
        
        for file_path in changed_files:
            # Skip non-Python files
            if not file_path.endswith(".py"):
                continue
                
            # Get file content
            file_content = context.get_file_content(file_path, context.head_ref)
            
            # Check line length
            self._check_line_length(file_content, file_path)
            
            try:
                # Parse the file
                tree = ast.parse(file_content)
                
                # Check docstrings
                if self.check_docstrings:
                    self._check_docstrings(tree, file_path)
                
                # Check naming conventions
                if self.check_naming:
                    self._check_naming_conventions(tree, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_line_length(self, content: str, file_path: str) -> None:
        """
        Check if any lines exceed the maximum length.
        
        Args:
            content: The file content.
            file_path: Path to the file being analyzed.
        """
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            if len(line) > self.max_line_length:
                self.create_result(
                    message=f"Line exceeds maximum length ({len(line)} > {self.max_line_length})",
                    file_path=file_path,
                    line_number=i + 1,
                    severity=RuleSeverity.INFO,
                )
    
    def _check_docstrings(self, tree: ast.AST, file_path: str) -> None:
        """
        Check if functions and classes have docstrings.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Skip private methods/classes
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                
                # Check if the node has a docstring
                has_docstring = False
                
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    if isinstance(node.body[0].value.value, str):
                        has_docstring = True
                
                if not has_docstring:
                    self.create_result(
                        message=f"{'Class' if isinstance(node, ast.ClassDef) else 'Function'} '{node.name}' is missing a docstring",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=RuleSeverity.INFO,
                    )
    
    def _check_naming_conventions(self, tree: ast.AST, file_path: str) -> None:
        """
        Check if names follow Python naming conventions.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        # Check class names (CapWords)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    self.create_result(
                        message=f"Class name '{node.name}' doesn't follow CapWords convention",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=RuleSeverity.INFO,
                    )
        
        # Check function and variable names (lowercase_with_underscores)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip special methods
                if node.name.startswith("__") and node.name.endswith("__"):
                    continue
                
                if not re.match(r"^[a-z][a-z0-9_]*$", node.name):
                    self.create_result(
                        message=f"Function name '{node.name}' doesn't follow lowercase_with_underscores convention",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=RuleSeverity.INFO,
                    )
            
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Skip constants
                        if target.id.isupper():
                            continue
                        
                        # Skip private variables
                        if target.id.startswith("_"):
                            continue
                        
                        if not re.match(r"^[a-z][a-z0-9_]*$", target.id):
                            self.create_result(
                                message=f"Variable name '{target.id}' doesn't follow lowercase_with_underscores convention",
                                file_path=file_path,
                                line_number=node.lineno,
                                severity=RuleSeverity.INFO,
                            )


class BestPracticeRule(BaseRule):
    """Rule for checking adherence to best practices."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the best practice rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="best_practice",
            name="Best Practice",
            description="Checks adherence to best practices",
            category=RuleCategory.IMPLEMENTATION,
            severity=RuleSeverity.WARNING,
            config=config,
        )

    def apply(self, context: Any) -> List[RuleResult]:
        """
        Apply the rule to the analysis context.

        Args:
            context: The analysis context containing the data to analyze.

        Returns:
            A list of rule results.
        """
        self.clear_results()
        
        # Get changed files from the context
        changed_files = context.get_changed_files()
        
        for file_path in changed_files:
            # Skip non-Python files
            if not file_path.endswith(".py"):
                continue
                
            # Get file content
            file_content = context.get_file_content(file_path, context.head_ref)
            
            try:
                # Parse the file
                tree = ast.parse(file_content)
                
                # Check for various best practices
                self._check_exception_handling(tree, file_path)
                self._check_mutable_defaults(tree, file_path)
                self._check_return_none(tree, file_path)
                self._check_explicit_return(tree, file_path)
                self._check_magic_numbers(tree, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_exception_handling(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for proper exception handling.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Check for empty except blocks
                for handler in node.handlers:
                    if not handler.body:
                        self.create_result(
                            message="Empty except block",
                            file_path=file_path,
                            line_number=handler.lineno,
                        )
                    
                    # Check for bare except
                    if handler.type is None:
                        self.create_result(
                            message="Bare except clause (should specify exception type)",
                            file_path=file_path,
                            line_number=handler.lineno,
                        )
                    
                    # Check for too broad exception handling
                    if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                        self.create_result(
                            message="Too broad exception handling (Exception)",
                            file_path=file_path,
                            line_number=handler.lineno,
                        )
    
    def _check_mutable_defaults(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for mutable default arguments.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for i, default in enumerate(node.args.defaults):
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        # Calculate the parameter index
                        param_index = len(node.args.args) - len(node.args.defaults) + i
                        param_name = node.args.args[param_index].arg
                        
                        self.create_result(
                            message=f"Mutable default argument '{param_name}' in function '{node.name}'",
                            file_path=file_path,
                            line_number=node.lineno,
                        )
    
    def _check_return_none(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for explicit 'return None' statements.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) and node.value.value is None:
                self.create_result(
                    message="Explicit 'return None' statement (can be simplified to 'return')",
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=RuleSeverity.INFO,
                )
    
    def _check_explicit_return(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for functions without explicit return statements.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if the function name suggests it's a command or action
                if any(keyword in node.name.lower() for keyword in ["do_", "process_", "handle_", "execute_"]):
                    continue
                
                # Check if the function has any return statements
                has_return = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Return):
                        has_return = True
                        break
                
                if not has_return and node.body:
                    self.create_result(
                        message=f"Function '{node.name}' has no explicit return statement",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=RuleSeverity.INFO,
                    )
    
    def _check_magic_numbers(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for magic numbers in code.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        # Skip common numbers that are not usually considered magic
        allowed_numbers = {0, 1, -1, 2, 10, 100}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip allowed numbers
                if node.value in allowed_numbers:
                    continue
                
                # Skip if the number is part of a slice
                if isinstance(node.parent, ast.Slice):
                    continue
                
                self.create_result(
                    message=f"Magic number '{node.value}' (consider using a named constant)",
                    file_path=file_path,
                    line_number=getattr(node, "lineno", 0),
                    severity=RuleSeverity.INFO,
                )


class LogicFlowRule(BaseRule):
    """Rule for analyzing code logic flow for issues."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the logic flow rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="logic_flow",
            name="Logic Flow",
            description="Analyzes code logic flow for issues",
            category=RuleCategory.IMPLEMENTATION,
            severity=RuleSeverity.WARNING,
            config=config,
        )

    def apply(self, context: Any) -> List[RuleResult]:
        """
        Apply the rule to the analysis context.

        Args:
            context: The analysis context containing the data to analyze.

        Returns:
            A list of rule results.
        """
        self.clear_results()
        
        # Get changed files from the context
        changed_files = context.get_changed_files()
        
        for file_path in changed_files:
            # Skip non-Python files
            if not file_path.endswith(".py"):
                continue
                
            # Get file content
            file_content = context.get_file_content(file_path, context.head_ref)
            
            try:
                # Parse the file
                tree = ast.parse(file_content)
                
                # Check for various logic flow issues
                self._check_nested_conditionals(tree, file_path)
                self._check_complex_boolean_expressions(tree, file_path)
                self._check_redundant_conditions(tree, file_path)
                self._check_early_returns(tree, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_nested_conditionals(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for deeply nested conditional statements.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        max_nesting = 3  # Maximum allowed nesting level
        
        def check_nesting(node, current_level=0):
            if current_level > max_nesting:
                self.create_result(
                    message=f"Deeply nested conditional (level {current_level} > {max_nesting})",
                    file_path=file_path,
                    line_number=node.lineno,
                )
            
            # Check if this node contains nested conditionals
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While)):
                    check_nesting(child, current_level + 1)
                else:
                    check_nesting(child, current_level)
        
        # Start checking from function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for child in node.body:
                    if isinstance(child, (ast.If, ast.For, ast.While)):
                        check_nesting(child, 1)
    
    def _check_complex_boolean_expressions(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for complex boolean expressions.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        max_operators = 3  # Maximum allowed boolean operators in a single expression
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp):
                # Count the number of operators
                operators = 1
                for value in node.values:
                    if isinstance(value, ast.BoolOp):
                        operators += 1
                
                if operators > max_operators:
                    self.create_result(
                        message=f"Complex boolean expression with {operators} operators (> {max_operators})",
                        file_path=file_path,
                        line_number=node.lineno,
                    )
    
    def _check_redundant_conditions(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for potentially redundant conditions.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for if-else with the same condition
                if node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    else_if = node.orelse[0]
                    
                    # Check if the conditions are negations of each other
                    if (
                        isinstance(node.test, ast.UnaryOp)
                        and isinstance(node.test.op, ast.Not)
                        and ast.dump(node.test.operand) == ast.dump(else_if.test)
                    ) or (
                        isinstance(else_if.test, ast.UnaryOp)
                        and isinstance(else_if.test.op, ast.Not)
                        and ast.dump(else_if.test.operand) == ast.dump(node.test)
                    ):
                        self.create_result(
                            message="Redundant conditions (if-else with negated conditions)",
                            file_path=file_path,
                            line_number=node.lineno,
                        )
    
    def _check_early_returns(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for missing early returns.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions with deep nesting that could benefit from early returns
                has_deep_nesting = False
                has_early_returns = False
                
                for i, stmt in enumerate(node.body):
                    # Check for deep nesting
                    if isinstance(stmt, ast.If) and stmt.orelse:
                        nested_level = 1
                        current = stmt
                        
                        while nested_level < 3 and current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                            nested_level += 1
                            current = current.orelse[0]
                        
                        if nested_level >= 2:
                            has_deep_nesting = True
                    
                    # Check for early returns
                    if i < len(node.body) - 1 and isinstance(stmt, ast.If):
                        for child in ast.walk(stmt):
                            if isinstance(child, ast.Return):
                                has_early_returns = True
                                break
                
                if has_deep_nesting and not has_early_returns:
                    self.create_result(
                        message=f"Function '{node.name}' has deep nesting but no early returns",
                        file_path=file_path,
                        line_number=node.lineno,
                    )

