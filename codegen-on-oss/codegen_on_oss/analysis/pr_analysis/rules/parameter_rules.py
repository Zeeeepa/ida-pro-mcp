"""
Parameter rules for PR static analysis.

This module defines rules for validating parameter usage, including missing parameters,
wrong parameter types, unused parameters, and inconsistent parameter usage.
"""

import ast
import inspect
from typing import Any, Dict, List, Optional, Set, Tuple

from codegen_on_oss.analysis.pr_analysis.rules.base_rule import (
    BaseRule,
    RuleCategory,
    RuleResult,
    RuleSeverity,
)


class MissingParameterRule(BaseRule):
    """Rule for detecting missing required parameters."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the missing parameter rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="missing_parameter",
            name="Missing Parameter",
            description="Detects missing required parameters",
            category=RuleCategory.PARAMETER,
            severity=RuleSeverity.ERROR,
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
                
                # Find all function definitions
                func_defs = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_defs[node.name] = node
                
                # Find all function calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Get the function name
                        func_name = None
                        if isinstance(node.func, ast.Name):
                            func_name = node.func.id
                        elif isinstance(node.func, ast.Attribute):
                            func_name = node.func.attr
                        
                        # Skip if we can't determine the function name
                        if not func_name:
                            continue
                        
                        # Skip if the function is not defined in this file
                        if func_name not in func_defs:
                            continue
                        
                        # Check for missing parameters
                        func_def = func_defs[func_name]
                        self._check_missing_parameters(func_def, node, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_missing_parameters(
        self, func_def: ast.FunctionDef, call_node: ast.Call, file_path: str
    ) -> None:
        """
        Check for missing parameters in a function call.
        
        Args:
            func_def: The function definition.
            call_node: The function call node.
            file_path: Path to the file being analyzed.
        """
        # Get required parameters from function definition
        required_params = []
        has_defaults = []
        
        for i, arg in enumerate(func_def.args.args):
            # Skip 'self' parameter for methods
            if i == 0 and arg.arg == "self":
                continue
            
            # Check if the parameter has a default value
            has_default = i >= len(func_def.args.args) - len(func_def.args.defaults)
            
            if not has_default:
                required_params.append(arg.arg)
            else:
                has_defaults.append(arg.arg)
        
        # Get provided parameters from function call
        provided_params = []
        
        # Positional arguments
        for i, arg in enumerate(call_node.args):
            if i < len(required_params):
                provided_params.append(required_params[i])
            elif i < len(required_params) + len(has_defaults):
                provided_params.append(has_defaults[i - len(required_params)])
        
        # Keyword arguments
        for keyword in call_node.keywords:
            provided_params.append(keyword.arg)
        
        # Check for missing required parameters
        for param in required_params:
            if param not in provided_params:
                self.create_result(
                    message=f"Missing required parameter '{param}' in call to '{func_def.name}'",
                    file_path=file_path,
                    line_number=call_node.lineno,
                )


class WrongParameterTypeRule(BaseRule):
    """Rule for detecting parameters with incorrect types."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the wrong parameter type rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="wrong_parameter_type",
            name="Wrong Parameter Type",
            description="Detects parameters with incorrect types",
            category=RuleCategory.PARAMETER,
            severity=RuleSeverity.ERROR,
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
                
                # Find all function definitions with type annotations
                func_defs_with_types = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if the function has type annotations
                        has_types = False
                        for arg in node.args.args:
                            if arg.annotation:
                                has_types = True
                                break
                        
                        if has_types:
                            func_defs_with_types[node.name] = node
                
                # Find all function calls to functions with type annotations
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Get the function name
                        func_name = None
                        if isinstance(node.func, ast.Name):
                            func_name = node.func.id
                        elif isinstance(node.func, ast.Attribute):
                            func_name = node.func.attr
                        
                        # Skip if we can't determine the function name
                        if not func_name:
                            continue
                        
                        # Skip if the function is not defined in this file or has no type annotations
                        if func_name not in func_defs_with_types:
                            continue
                        
                        # Check for wrong parameter types
                        func_def = func_defs_with_types[func_name]
                        self._check_parameter_types(func_def, node, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_parameter_types(
        self, func_def: ast.FunctionDef, call_node: ast.Call, file_path: str
    ) -> None:
        """
        Check for wrong parameter types in a function call.
        
        Args:
            func_def: The function definition.
            call_node: The function call node.
            file_path: Path to the file being analyzed.
        """
        # Get parameter types from function definition
        param_types = {}
        
        for i, arg in enumerate(func_def.args.args):
            if arg.annotation:
                param_types[arg.arg] = arg.annotation
        
        # Check positional arguments
        for i, arg in enumerate(call_node.args):
            # Skip 'self' parameter for methods
            if i == 0 and len(func_def.args.args) > 0 and func_def.args.args[0].arg == "self":
                continue
            
            # Get the parameter name and type
            param_index = i
            if len(func_def.args.args) > 0 and func_def.args.args[0].arg == "self":
                param_index += 1
            
            if param_index < len(func_def.args.args):
                param_name = func_def.args.args[param_index].arg
                param_type = param_types.get(param_name)
                
                if param_type:
                    self._check_argument_type(arg, param_type, param_name, func_def.name, call_node.lineno, file_path)
        
        # Check keyword arguments
        for keyword in call_node.keywords:
            param_name = keyword.arg
            param_type = param_types.get(param_name)
            
            if param_type:
                self._check_argument_type(keyword.value, param_type, param_name, func_def.name, call_node.lineno, file_path)
    
    def _check_argument_type(
        self, arg_node: ast.AST, param_type_node: ast.AST, param_name: str, func_name: str, line_number: int, file_path: str
    ) -> None:
        """
        Check if an argument matches the expected parameter type.
        
        Args:
            arg_node: The argument node.
            param_type_node: The parameter type annotation node.
            param_name: The parameter name.
            func_name: The function name.
            line_number: The line number of the function call.
            file_path: Path to the file being analyzed.
        """
        # Get the expected type as a string
        expected_type = self._get_type_as_string(param_type_node)
        
        # Get the actual type based on the argument node
        actual_type = self._infer_arg_type(arg_node)
        
        # Check if the types are compatible
        if actual_type and expected_type and not self._are_types_compatible(actual_type, expected_type):
            self.create_result(
                message=f"Parameter '{param_name}' in call to '{func_name}' has wrong type: expected '{expected_type}', got '{actual_type}'",
                file_path=file_path,
                line_number=line_number,
            )
    
    def _get_type_as_string(self, type_node: ast.AST) -> Optional[str]:
        """
        Convert a type annotation node to a string.
        
        Args:
            type_node: The type annotation node.
            
        Returns:
            The type as a string, or None if it can't be determined.
        """
        if isinstance(type_node, ast.Name):
            return type_node.id
        elif isinstance(type_node, ast.Attribute):
            if isinstance(type_node.value, ast.Name):
                return f"{type_node.value.id}.{type_node.attr}"
        elif isinstance(type_node, ast.Subscript):
            if isinstance(type_node.value, ast.Name):
                return f"{type_node.value.id}[...]"
        
        return None
    
    def _infer_arg_type(self, arg_node: ast.AST) -> Optional[str]:
        """
        Infer the type of an argument.
        
        Args:
            arg_node: The argument node.
            
        Returns:
            The inferred type as a string, or None if it can't be determined.
        """
        if isinstance(arg_node, ast.Constant):
            return type(arg_node.value).__name__
        elif isinstance(arg_node, ast.List):
            return "list"
        elif isinstance(arg_node, ast.Dict):
            return "dict"
        elif isinstance(arg_node, ast.Set):
            return "set"
        elif isinstance(arg_node, ast.Tuple):
            return "tuple"
        elif isinstance(arg_node, ast.Name):
            # Can't determine the type of a variable without more analysis
            return None
        elif isinstance(arg_node, ast.Call):
            if isinstance(arg_node.func, ast.Name):
                return arg_node.func.id
            elif isinstance(arg_node.func, ast.Attribute):
                if isinstance(arg_node.func.value, ast.Name):
                    return f"{arg_node.func.value.id}.{arg_node.func.attr}"
        
        return None
    
    def _are_types_compatible(self, actual_type: str, expected_type: str) -> bool:
        """
        Check if two types are compatible.
        
        Args:
            actual_type: The actual type.
            expected_type: The expected type.
            
        Returns:
            True if the types are compatible, False otherwise.
        """
        # Simple compatibility checks
        if actual_type == expected_type:
            return True
        
        # Handle some common cases
        if expected_type == "int" and actual_type == "float":
            return False
        if expected_type == "float" and actual_type == "int":
            return True
        if expected_type == "str" and actual_type in ("int", "float", "bool"):
            return False
        if expected_type == "bool" and actual_type in ("int", "float"):
            return True
        
        # Handle container types
        if expected_type.startswith(("list", "dict", "set", "tuple")) and actual_type == expected_type.split("[")[0]:
            return True
        
        # By default, assume they might be compatible
        return True


class UnusedParameterRule(BaseRule):
    """Rule for detecting parameters that are defined but not used."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the unused parameter rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="unused_parameter",
            name="Unused Parameter",
            description="Detects parameters that are defined but not used",
            category=RuleCategory.PARAMETER,
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
                
                # Find all function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        self._check_unused_parameters(node, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_unused_parameters(self, func_node: ast.FunctionDef, file_path: str) -> None:
        """
        Check for unused parameters in a function.
        
        Args:
            func_node: The function node to check.
            file_path: Path to the file being analyzed.
        """
        # Get all parameters
        params = []
        for i, arg in enumerate(func_node.args.args):
            # Skip 'self' parameter for methods
            if i == 0 and arg.arg == "self":
                continue
            
            params.append(arg.arg)
        
        # Add *args and **kwargs parameters
        if func_node.args.vararg:
            params.append(func_node.args.vararg.arg)
        if func_node.args.kwarg:
            params.append(func_node.args.kwarg.arg)
        
        # Find all used names in the function body
        used_names = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
        
        # Check for unused parameters
        for param in params:
            if param not in used_names:
                # Skip special cases
                if param.startswith("_") or func_node.name.startswith("test_"):
                    continue
                
                self.create_result(
                    message=f"Unused parameter '{param}' in function '{func_node.name}'",
                    file_path=file_path,
                    line_number=func_node.lineno,
                )


class InconsistentParameterRule(BaseRule):
    """Rule for detecting inconsistent parameter usage across similar functions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the inconsistent parameter rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="inconsistent_parameter",
            name="Inconsistent Parameter",
            description="Detects inconsistent parameter usage across similar functions",
            category=RuleCategory.PARAMETER,
            severity=RuleSeverity.WARNING,
            config=config,
        )
        
        # Default configuration
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)

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
                
                # Find all function definitions
                func_defs = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_defs.append(node)
                
                # Group similar functions
                similar_funcs = self._group_similar_functions(func_defs)
                
                # Check for inconsistent parameter usage within each group
                for group in similar_funcs:
                    self._check_inconsistent_parameters(group, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _group_similar_functions(self, func_defs: List[ast.FunctionDef]) -> List[List[ast.FunctionDef]]:
        """
        Group similar functions based on name similarity.
        
        Args:
            func_defs: List of function definitions.
            
        Returns:
            List of groups of similar functions.
        """
        groups = []
        
        # Group functions with similar names
        for i, func1 in enumerate(func_defs):
            found_group = False
            
            for group in groups:
                for func2 in group:
                    if self._are_functions_similar(func1, func2):
                        group.append(func1)
                        found_group = True
                        break
                
                if found_group:
                    break
            
            if not found_group:
                groups.append([func1])
        
        # Filter out groups with only one function
        return [group for group in groups if len(group) > 1]
    
    def _are_functions_similar(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> bool:
        """
        Check if two functions are similar based on their names.
        
        Args:
            func1: The first function.
            func2: The second function.
            
        Returns:
            True if the functions are similar, False otherwise.
        """
        # Check if the function names are similar
        name1 = func1.name.lower()
        name2 = func2.name.lower()
        
        # Calculate similarity based on common substrings
        similarity = self._calculate_name_similarity(name1, name2)
        
        return similarity >= self.similarity_threshold
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two function names.
        
        Args:
            name1: The first function name.
            name2: The second function name.
            
        Returns:
            A similarity score between 0 and 1.
        """
        # Simple approach: count matching characters
        matches = 0
        for c1, c2 in zip(name1, name2):
            if c1 == c2:
                matches += 1
        
        # Calculate similarity
        return matches / max(len(name1), len(name2))
    
    def _check_inconsistent_parameters(self, funcs: List[ast.FunctionDef], file_path: str) -> None:
        """
        Check for inconsistent parameter usage across similar functions.
        
        Args:
            funcs: List of similar functions.
            file_path: Path to the file being analyzed.
        """
        # Get parameter lists for each function
        param_lists = []
        for func in funcs:
            params = []
            for i, arg in enumerate(func.args.args):
                # Skip 'self' parameter for methods
                if i == 0 and arg.arg == "self":
                    continue
                
                params.append(arg.arg)
            
            param_lists.append((func, params))
        
        # Check for inconsistent parameter names
        for i, (func1, params1) in enumerate(param_lists):
            for j, (func2, params2) in enumerate(param_lists):
                if i >= j:
                    continue
                
                # Skip if the functions have different number of parameters
                if len(params1) != len(params2):
                    continue
                
                # Check for parameter name differences
                for k, (param1, param2) in enumerate(zip(params1, params2)):
                    if param1 != param2:
                        self.create_result(
                            message=f"Inconsistent parameter name in similar functions: '{func1.name}' uses '{param1}' while '{func2.name}' uses '{param2}' for parameter {k+1}",
                            file_path=file_path,
                            line_number=func1.lineno,
                        )

