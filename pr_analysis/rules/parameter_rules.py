"""
Parameter rules for PR static analysis.

This module provides rules for checking function parameters.
"""

import ast
import re
from typing import List, ClassVar, Dict, Any, Set

from .base_rule import BaseRule
from ..core.analysis_context import PRAnalysisContext, AnalysisResult


class MissingTypeHints(BaseRule):
    """Rule that checks for missing type hints in function parameters."""
    
    RULE_ID: ClassVar[str] = "parameter.missing_type_hints"
    RULE_NAME: ClassVar[str] = "Missing Type Hints"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for missing type hints in function parameters"
    RULE_CATEGORY: ClassVar[str] = "parameter"
    RULE_PRIORITY: ClassVar[int] = 3
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for missing type hints.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        
        for file_change in context.get_code_files():
            if file_change.status == "removed":
                continue
                
            # Only check Python files
            if not file_change.filename.endswith(".py"):
                continue
                
            # Skip files that are too large
            if file_change.patch and len(file_change.patch) > 1000000:  # 1MB
                continue
                
            # Parse the file
            try:
                tree = self._get_ast_from_patch(file_change.patch)
                if not tree:
                    continue
                    
                # Find all function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if the function is in the changed lines
                        if node.lineno in file_change.changed_lines:
                            # Check for missing type hints
                            missing_hints = self._check_type_hints(node)
                            if missing_hints:
                                params_str = ", ".join(missing_hints)
                                results.append(AnalysisResult(
                                    rule_id=self.RULE_ID,
                                    rule_name=self.RULE_NAME,
                                    severity="warning",
                                    message=f"Function '{node.name}' is missing type hints for parameters: {params_str}",
                                    file=file_change.filename,
                                    line=node.lineno,
                                    suggested_fix=self._generate_type_hint_suggestion(node),
                                    metadata={
                                        "function_name": node.name,
                                        "missing_hints": missing_hints,
                                    },
                                ))
            except SyntaxError:
                # Skip files with syntax errors
                continue
                
        return results
        
    def _get_ast_from_patch(self, patch: str) -> Optional[ast.Module]:
        """
        Extract Python code from a patch and parse it into an AST.
        
        Args:
            patch: The patch text
            
        Returns:
            An AST module, or None if parsing failed
        """
        # Extract added lines from the patch
        added_lines = []
        for line in patch.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])  # Remove the "+" prefix
                
        if not added_lines:
            return None
            
        # Parse the code
        code = "\n".join(added_lines)
        try:
            return ast.parse(code)
        except SyntaxError:
            return None
            
    def _check_type_hints(self, node: ast.FunctionDef) -> List[str]:
        """
        Check for missing type hints in a function definition.
        
        Args:
            node: The function definition node
            
        Returns:
            A list of parameter names with missing type hints
        """
        missing_hints = []
        
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                missing_hints.append(arg.arg)
                
        return missing_hints
        
    def _generate_type_hint_suggestion(self, node: ast.FunctionDef) -> str:
        """
        Generate a suggested fix for missing type hints.
        
        Args:
            node: The function definition node
            
        Returns:
            A suggested fix
        """
        # This is a simplified suggestion that just adds "Any" for all missing hints
        args = []
        for arg in node.args.args:
            if arg.arg == "self" or arg.arg == "cls":
                args.append(arg.arg)
            elif arg.annotation is None:
                args.append(f"{arg.arg}: Any")
            else:
                # Keep existing annotation
                args.append(f"{arg.arg}: {ast.unparse(arg.annotation)}")
                
        return f"from typing import Any\n\ndef {node.name}({', '.join(args)}):"


class DefaultParameterMutable(BaseRule):
    """Rule that checks for mutable default parameters."""
    
    RULE_ID: ClassVar[str] = "parameter.default_mutable"
    RULE_NAME: ClassVar[str] = "Mutable Default Parameter"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for mutable default parameters in functions"
    RULE_CATEGORY: ClassVar[str] = "parameter"
    RULE_PRIORITY: ClassVar[int] = 4
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for mutable default parameters.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        
        for file_change in context.get_code_files():
            if file_change.status == "removed":
                continue
                
            # Only check Python files
            if not file_change.filename.endswith(".py"):
                continue
                
            # Skip files that are too large
            if file_change.patch and len(file_change.patch) > 1000000:  # 1MB
                continue
                
            # Parse the file
            try:
                tree = self._get_ast_from_patch(file_change.patch)
                if not tree:
                    continue
                    
                # Find all function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if the function is in the changed lines
                        if node.lineno in file_change.changed_lines:
                            # Check for mutable default parameters
                            mutable_defaults = self._check_mutable_defaults(node)
                            if mutable_defaults:
                                params_str = ", ".join(mutable_defaults)
                                results.append(AnalysisResult(
                                    rule_id=self.RULE_ID,
                                    rule_name=self.RULE_NAME,
                                    severity="warning",
                                    message=f"Function '{node.name}' has mutable default parameters: {params_str}",
                                    file=file_change.filename,
                                    line=node.lineno,
                                    suggested_fix=self._generate_mutable_default_suggestion(node, mutable_defaults),
                                    metadata={
                                        "function_name": node.name,
                                        "mutable_defaults": mutable_defaults,
                                    },
                                ))
            except SyntaxError:
                # Skip files with syntax errors
                continue
                
        return results
        
    def _get_ast_from_patch(self, patch: str) -> Optional[ast.Module]:
        """
        Extract Python code from a patch and parse it into an AST.
        
        Args:
            patch: The patch text
            
        Returns:
            An AST module, or None if parsing failed
        """
        # Extract added lines from the patch
        added_lines = []
        for line in patch.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])  # Remove the "+" prefix
                
        if not added_lines:
            return None
            
        # Parse the code
        code = "\n".join(added_lines)
        try:
            return ast.parse(code)
        except SyntaxError:
            return None
            
    def _check_mutable_defaults(self, node: ast.FunctionDef) -> List[str]:
        """
        Check for mutable default parameters in a function definition.
        
        Args:
            node: The function definition node
            
        Returns:
            A list of parameter names with mutable defaults
        """
        mutable_defaults = []
        
        # Check for default values
        defaults = node.args.defaults
        if not defaults:
            return []
            
        # Get the arguments that have default values
        args_with_defaults = node.args.args[-len(defaults):]
        
        for i, default in enumerate(defaults):
            arg_name = args_with_defaults[i].arg
            
            # Check if the default is a mutable type
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                mutable_defaults.append(arg_name)
            elif isinstance(default, ast.Call) and isinstance(default.func, ast.Name):
                if default.func.id in ["list", "dict", "set"]:
                    mutable_defaults.append(arg_name)
                    
        return mutable_defaults
        
    def _generate_mutable_default_suggestion(self, node: ast.FunctionDef, 
                                          mutable_params: List[str]) -> str:
        """
        Generate a suggested fix for mutable default parameters.
        
        Args:
            node: The function definition node
            mutable_params: List of parameter names with mutable defaults
            
        Returns:
            A suggested fix
        """
        # Create a set of mutable parameter names for quick lookup
        mutable_param_set = set(mutable_params)
        
        # Generate the function signature
        args = []
        for arg in node.args.args:
            if arg.arg in mutable_param_set:
                args.append(f"{arg.arg}=None")
            elif arg.annotation is None:
                args.append(arg.arg)
            else:
                # Keep existing annotation
                args.append(f"{arg.arg}: {ast.unparse(arg.annotation)}")
                
        # Generate the function body with initialization of mutable parameters
        body = []
        for param in mutable_params:
            body.append(f"    if {param} is None:")
            body.append(f"        {param} = []  # or {} or set() as appropriate")
            
        return f"def {node.name}({', '.join(args)}):\n" + "\n".join(body)

