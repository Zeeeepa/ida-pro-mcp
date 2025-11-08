"""
Parameter validation rules for the PR static analysis system.

This module contains rules for detecting parameter problems, such as
incorrect parameter types, missing parameters, and inconsistent parameter usage.
"""
import re
import ast
from typing import List, Dict, Any, Optional, Set, Tuple

from ..core import BaseRule, AnalysisResult, AnalysisContext


class IncorrectParameterTypeRule(BaseRule):
    """
    Rule for detecting incorrect parameter types.
    """
    def __init__(self):
        """Initialize the incorrect parameter type rule."""
        super().__init__(
            name="incorrect_parameter_type",
            description="Detects incorrect parameter types",
            severity="error"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect incorrect parameter types.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in context.get_changed_files():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            
            try:
                # Parse the file into an AST
                tree = ast.parse(content)
                
                # Visit all function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for type annotations
                        for arg in node.args.args:
                            if arg.annotation is None:
                                continue  # No type annotation
                            
                            # Check function body for type inconsistencies
                            self._check_type_usage(node, arg, file_path, results)
            
            except SyntaxError:
                # If the file has syntax errors, we can't parse it
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains syntax errors, cannot analyze parameter types",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        return results
    
    def _check_type_usage(self, func_node: ast.FunctionDef, arg: ast.arg, file_path: str, results: List[AnalysisResult]) -> None:
        """
        Check if a parameter is used consistently with its type annotation.
        
        Args:
            func_node: AST node for the function definition
            arg: AST node for the parameter
            file_path: Path to the file being analyzed
            results: List to append results to
        """
        arg_name = arg.arg
        
        # Skip self and cls
        if arg_name in ('self', 'cls'):
            return
        
        # Get the type annotation as a string
        if isinstance(arg.annotation, ast.Name):
            type_name = arg.annotation.id
        elif isinstance(arg.annotation, ast.Subscript):
            # Handle generic types like List[int]
            if isinstance(arg.annotation.value, ast.Name):
                type_name = arg.annotation.value.id
            else:
                return  # Complex type annotation, skip
        else:
            return  # Complex type annotation, skip
        
        # Look for operations that might be inconsistent with the type
        for node in ast.walk(func_node):
            # Check for operations on the parameter
            if isinstance(node, ast.BinOp) and isinstance(node.left, ast.Name) and node.left.id == arg_name:
                # Check for operations that might be inconsistent with the type
                if type_name in ('str', 'bytes') and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                    if isinstance(node.op, ast.Add) and type_name == 'str':
                        continue  # String concatenation is valid
                    
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Parameter '{arg_name}' is annotated as '{type_name}' but is used in an arithmetic operation",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=self.severity
                    ))
                
                elif type_name in ('int', 'float') and isinstance(node.op, ast.Mod) and not isinstance(node.right, ast.Str):
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Parameter '{arg_name}' is annotated as '{type_name}' but is used in a modulo operation with a non-string",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=self.severity
                    ))
            
            # Check for method calls that might be inconsistent with the type
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == arg_name:
                method_name = node.func.attr
                
                # Check for methods that might be inconsistent with the type
                if type_name == 'int' and method_name in ('lower', 'upper', 'strip', 'split'):
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Parameter '{arg_name}' is annotated as 'int' but '{method_name}' method is called on it, which is a string method",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=self.severity
                    ))
                
                elif type_name == 'str' and method_name in ('items', 'keys', 'values'):
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Parameter '{arg_name}' is annotated as 'str' but '{method_name}' method is called on it, which is a dictionary method",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=self.severity
                    ))
                
                elif type_name == 'list' and method_name in ('items', 'keys', 'values'):
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Parameter '{arg_name}' is annotated as 'list' but '{method_name}' method is called on it, which is a dictionary method",
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=self.severity
                    ))


class MissingParameterRule(BaseRule):
    """
    Rule for detecting missing required parameters.
    """
    def __init__(self):
        """Initialize the missing parameter rule."""
        super().__init__(
            name="missing_parameter",
            description="Detects missing required parameters",
            severity="error"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect missing required parameters.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in context.get_changed_files():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            
            try:
                # Parse the file into an AST
                tree = ast.parse(content)
                
                # Get all function definitions
                function_defs = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_defs[node.name] = node
                
                # Check all function calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in function_defs:
                        func_name = node.func.id
                        func_def = function_defs[func_name]
                        
                        # Check if all required parameters are provided
                        self._check_missing_params(func_def, node, file_path, results)
            
            except SyntaxError:
                # If the file has syntax errors, we can't parse it
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains syntax errors, cannot analyze parameter usage",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        return results
    
    def _check_missing_params(self, func_def: ast.FunctionDef, call_node: ast.Call, file_path: str, results: List[AnalysisResult]) -> None:
        """
        Check if all required parameters are provided in a function call.
        
        Args:
            func_def: AST node for the function definition
            call_node: AST node for the function call
            file_path: Path to the file being analyzed
            results: List to append results to
        """
        # Get all required parameters (those without default values)
        required_params = []
        for i, arg in enumerate(func_def.args.args):
            # Skip self and cls
            if i == 0 and arg.arg in ('self', 'cls'):
                continue
            
            # Check if this parameter has a default value
            default_offset = len(func_def.args.args) - len(func_def.args.defaults)
            if i >= default_offset:
                # This parameter has a default value
                continue
            
            required_params.append(arg.arg)
        
        # Check if all required parameters are provided
        provided_params = set()
        
        # Add positional arguments
        for i, arg in enumerate(call_node.args):
            if i < len(required_params):
                provided_params.add(required_params[i])
        
        # Add keyword arguments
        for keyword in call_node.keywords:
            provided_params.add(keyword.arg)
        
        # Check for missing parameters
        missing_params = set(required_params) - provided_params
        if missing_params:
            results.append(AnalysisResult(
                rule_name=self.name,
                message=f"Call to function '{func_def.name}' is missing required parameters: {', '.join(missing_params)}",
                file_path=file_path,
                line_number=call_node.lineno,
                severity=self.severity
            ))


class InconsistentParameterRule(BaseRule):
    """
    Rule for detecting inconsistent parameter usage.
    """
    def __init__(self):
        """Initialize the inconsistent parameter rule."""
        super().__init__(
            name="inconsistent_parameter",
            description="Detects inconsistent parameter usage",
            severity="warning"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect inconsistent parameter usage.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        # Track function signatures across files
        function_signatures: Dict[str, List[Tuple[str, int, List[str]]]] = {}
        
        for file_path in context.get_changed_files():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            
            try:
                # Parse the file into an AST
                tree = ast.parse(content)
                
                # Get all function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private methods
                        if node.name.startswith('_'):
                            continue
                        
                        # Get parameter names
                        param_names = []
                        for arg in node.args.args:
                            # Skip self and cls
                            if arg.arg in ('self', 'cls'):
                                continue
                            
                            param_names.append(arg.arg)
                        
                        # Add to function signatures
                        if node.name not in function_signatures:
                            function_signatures[node.name] = []
                        
                        function_signatures[node.name].append((file_path, node.lineno, param_names))
            
            except SyntaxError:
                # If the file has syntax errors, we can't parse it
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains syntax errors, cannot analyze parameter usage",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        # Check for inconsistent parameter names
        for func_name, signatures in function_signatures.items():
            if len(signatures) <= 1:
                continue  # Only one implementation, no inconsistency
            
            # Check if all implementations have the same parameter names
            first_signature = signatures[0][2]
            for file_path, line_number, param_names in signatures[1:]:
                if len(param_names) != len(first_signature):
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Function '{func_name}' has inconsistent number of parameters: {len(first_signature)} vs {len(param_names)}",
                        file_path=file_path,
                        line_number=line_number,
                        severity=self.severity
                    ))
                    continue
                
                for i, (param1, param2) in enumerate(zip(first_signature, param_names)):
                    if param1 != param2:
                        results.append(AnalysisResult(
                            rule_name=self.name,
                            message=f"Function '{func_name}' has inconsistent parameter name at position {i+1}: '{param1}' vs '{param2}'",
                            file_path=file_path,
                            line_number=line_number,
                            severity=self.severity
                        ))
        
        return results

