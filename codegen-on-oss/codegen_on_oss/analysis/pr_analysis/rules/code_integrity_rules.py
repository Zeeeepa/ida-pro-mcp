"""
Code integrity rules for PR static analysis.

This module defines rules for detecting code integrity issues such as syntax errors,
missing imports, undefined references, duplicate code, and dead code.
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


class SyntaxErrorRule(BaseRule):
    """Rule for detecting syntax errors in code."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the syntax error rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="syntax_error",
            name="Syntax Error",
            description="Detects syntax errors in code",
            category=RuleCategory.CODE_INTEGRITY,
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
            
            # Check for syntax errors
            try:
                ast.parse(file_content)
            except SyntaxError as e:
                self.create_result(
                    message=f"Syntax error: {str(e)}",
                    file_path=file_path,
                    line_number=e.lineno or 1,
                )
        
        return self.get_results()


class MissingImportRule(BaseRule):
    """Rule for detecting missing imports in code."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the missing import rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="missing_import",
            name="Missing Import",
            description="Detects missing imports in code",
            category=RuleCategory.CODE_INTEGRITY,
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
                
                # Find all imports
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.add(name.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])
                
                # Find all names used
                names_used = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                        names_used.add(node.id)
                
                # Check for potential missing imports
                # This is a simplified check and may produce false positives
                for name in names_used:
                    if (
                        name[0].isupper()  # Likely a class or module
                        and name not in imports
                        and name not in dir(__builtins__)
                    ):
                        # Find the line number where the name is used
                        for node in ast.walk(tree):
                            if (
                                isinstance(node, ast.Name)
                                and node.id == name
                                and isinstance(node.ctx, ast.Load)
                            ):
                                self.create_result(
                                    message=f"Potential missing import for '{name}'",
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    severity=RuleSeverity.WARNING,
                                )
                                break
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()


class UndefinedReferenceRule(BaseRule):
    """Rule for detecting references to undefined variables/functions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the undefined reference rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="undefined_reference",
            name="Undefined Reference",
            description="Detects references to undefined variables/functions",
            category=RuleCategory.CODE_INTEGRITY,
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
                
                # Collect defined names in each scope
                defined_names = self._collect_defined_names(tree)
                
                # Check for undefined references
                self._check_undefined_references(tree, defined_names, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _collect_defined_names(self, tree: ast.AST) -> Dict[ast.AST, Set[str]]:
        """
        Collect defined names in each scope.
        
        Args:
            tree: The AST to analyze.
            
        Returns:
            A dictionary mapping scopes to sets of defined names.
        """
        defined_names = {}
        
        # Global scope
        global_names = set()
        defined_names[tree] = global_names
        
        # Add built-in names
        global_names.update(dir(__builtins__))
        
        # Add imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    global_names.add(name.name.split(".")[0])
                    if name.asname:
                        global_names.add(name.asname)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    global_names.add(name.name)
                    if name.asname:
                        global_names.add(name.asname)
        
        # Add function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                global_names.add(node.name)
                
                # Function/class scope
                func_names = set(global_names)  # Inherit from global scope
                defined_names[node] = func_names
                
                # Add parameters for functions
                if isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        func_names.add(arg.arg)
                    if node.args.vararg:
                        func_names.add(node.args.vararg.arg)
                    if node.args.kwarg:
                        func_names.add(node.args.kwarg.arg)
                
                # Add variables defined in the function/class
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                func_names.add(target.id)
        
        return defined_names
    
    def _check_undefined_references(
        self, node: ast.AST, defined_names: Dict[ast.AST, Set[str]], file_path: str
    ) -> None:
        """
        Check for undefined references in a node.
        
        Args:
            node: The AST node to check.
            defined_names: Dictionary mapping scopes to sets of defined names.
            file_path: Path to the file being analyzed.
        """
        # Find the scope for this node
        scope = None
        for potential_scope in defined_names:
            if self._is_node_in_scope(node, potential_scope):
                scope = potential_scope
                break
        
        if scope is None:
            scope = list(defined_names.keys())[0]  # Global scope
        
        # Check for undefined names
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined_names[scope]:
                self.create_result(
                    message=f"Undefined reference to '{node.id}'",
                    file_path=file_path,
                    line_number=node.lineno,
                )
        
        # Recursively check children
        for child in ast.iter_child_nodes(node):
            self._check_undefined_references(child, defined_names, file_path)
    
    def _is_node_in_scope(self, node: ast.AST, scope: ast.AST) -> bool:
        """
        Check if a node is in a scope.
        
        Args:
            node: The AST node to check.
            scope: The scope to check against.
            
        Returns:
            True if the node is in the scope, False otherwise.
        """
        if scope == node:
            return True
        
        for child in ast.iter_child_nodes(scope):
            if self._is_node_in_scope(node, child):
                return True
        
        return False


class DuplicateCodeRule(BaseRule):
    """Rule for detecting duplicated code blocks."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the duplicate code rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="duplicate_code",
            name="Duplicate Code",
            description="Detects duplicated code blocks",
            category=RuleCategory.CODE_INTEGRITY,
            severity=RuleSeverity.WARNING,
            config=config,
        )
        
        # Default configuration
        self.min_lines = self.config.get("min_lines", 5)
        self.min_similarity = self.config.get("min_similarity", 0.8)

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
        
        # Group files by extension
        files_by_ext = {}
        for file_path in changed_files:
            ext = file_path.split(".")[-1] if "." in file_path else ""
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file_path)
        
        # Check for duplicates within each file type
        for ext, files in files_by_ext.items():
            # Skip if only one file of this type
            if len(files) < 2:
                continue
            
            # Extract code blocks from each file
            blocks_by_file = {}
            for file_path in files:
                file_content = context.get_file_content(file_path, context.head_ref)
                blocks_by_file[file_path] = self._extract_code_blocks(file_content)
            
            # Compare blocks across files
            for i, (file1, blocks1) in enumerate(blocks_by_file.items()):
                for j, (file2, blocks2) in enumerate(blocks_by_file.items()):
                    # Skip self-comparison and avoid duplicate comparisons
                    if i >= j:
                        continue
                    
                    # Compare blocks
                    for block1_info in blocks1:
                        block1, start_line1 = block1_info
                        for block2_info in blocks2:
                            block2, start_line2 = block2_info
                            
                            similarity = self._calculate_similarity(block1, block2)
                            if similarity >= self.min_similarity:
                                self.create_result(
                                    message=f"Duplicate code block found (similarity: {similarity:.2f})",
                                    file_path=file1,
                                    line_number=start_line1,
                                    additional_data={
                                        "duplicate_file": file2,
                                        "duplicate_line": start_line2,
                                        "similarity": similarity,
                                    },
                                )
        
        return self.get_results()
    
    def _extract_code_blocks(self, content: str) -> List[Tuple[str, int]]:
        """
        Extract code blocks from file content.
        
        Args:
            content: The file content.
            
        Returns:
            A list of tuples containing code blocks and their starting line numbers.
        """
        lines = content.split("\n")
        blocks = []
        
        # Simple approach: extract blocks of min_lines consecutive non-empty lines
        current_block = []
        start_line = 0
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            if stripped_line and not stripped_line.startswith(("#", "//", "/*", "*", "*/")):
                if not current_block:
                    start_line = i + 1
                current_block.append(line)
            else:
                if len(current_block) >= self.min_lines:
                    blocks.append(("\n".join(current_block), start_line))
                current_block = []
        
        # Don't forget the last block
        if len(current_block) >= self.min_lines:
            blocks.append(("\n".join(current_block), start_line))
        
        return blocks
    
    def _calculate_similarity(self, block1: str, block2: str) -> float:
        """
        Calculate similarity between two code blocks.
        
        Args:
            block1: The first code block.
            block2: The second code block.
            
        Returns:
            A similarity score between 0 and 1.
        """
        # Simple approach: count matching lines
        lines1 = block1.split("\n")
        lines2 = block2.split("\n")
        
        # Normalize lines (remove whitespace, comments)
        norm_lines1 = [self._normalize_line(line) for line in lines1]
        norm_lines2 = [self._normalize_line(line) for line in lines2]
        
        # Count matching lines
        matches = 0
        for line in norm_lines1:
            if line in norm_lines2:
                matches += 1
        
        # Calculate similarity
        return matches / max(len(norm_lines1), len(norm_lines2))
    
    def _normalize_line(self, line: str) -> str:
        """
        Normalize a line for comparison.
        
        Args:
            line: The line to normalize.
            
        Returns:
            The normalized line.
        """
        # Remove comments
        line = re.sub(r"#.*$", "", line)
        line = re.sub(r"//.*$", "", line)
        
        # Remove whitespace
        line = line.strip()
        
        return line


class DeadCodeRule(BaseRule):
    """Rule for detecting code that is never executed."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the dead code rule.

        Args:
            config: Rule-specific configuration.
        """
        super().__init__(
            rule_id="dead_code",
            name="Dead Code",
            description="Detects code that is never executed",
            category=RuleCategory.CODE_INTEGRITY,
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
                
                # Check for unreachable code
                self._check_unreachable_code(tree, file_path)
                
                # Check for unused functions and classes
                self._check_unused_definitions(tree, file_path)
                
            except SyntaxError:
                # Skip files with syntax errors, as they will be caught by SyntaxErrorRule
                pass
        
        return self.get_results()
    
    def _check_unreachable_code(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for unreachable code in a file.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        for node in ast.walk(tree):
            # Check for code after return/break/continue
            if isinstance(node, ast.FunctionDef):
                self._check_unreachable_in_function(node, file_path)
            
            # Check for if statements with always True/False conditions
            if isinstance(node, ast.If):
                self._check_constant_if_condition(node, file_path)
    
    def _check_unreachable_in_function(self, func_node: ast.FunctionDef, file_path: str) -> None:
        """
        Check for unreachable code in a function.
        
        Args:
            func_node: The function node to check.
            file_path: Path to the file being analyzed.
        """
        for i, stmt in enumerate(func_node.body):
            # Check if this statement is a return/break/continue
            is_terminator = (
                isinstance(stmt, ast.Return)
                or isinstance(stmt, ast.Break)
                or isinstance(stmt, ast.Continue)
                or (isinstance(stmt, ast.Raise) and not isinstance(stmt.exc, ast.Name))
            )
            
            # If it's a terminator and not the last statement, the following code is unreachable
            if is_terminator and i < len(func_node.body) - 1:
                next_stmt = func_node.body[i + 1]
                self.create_result(
                    message="Unreachable code after return/break/continue/raise statement",
                    file_path=file_path,
                    line_number=next_stmt.lineno,
                )
    
    def _check_constant_if_condition(self, if_node: ast.If, file_path: str) -> None:
        """
        Check for if statements with constant conditions.
        
        Args:
            if_node: The if node to check.
            file_path: Path to the file being analyzed.
        """
        # Check if the condition is a constant
        if isinstance(if_node.test, ast.Constant):
            if if_node.test.value:
                # Always True, else branch is dead
                if if_node.orelse:
                    self.create_result(
                        message="Unreachable code in 'else' branch (condition is always True)",
                        file_path=file_path,
                        line_number=if_node.orelse[0].lineno,
                    )
            else:
                # Always False, if branch is dead
                self.create_result(
                    message="Unreachable code in 'if' branch (condition is always False)",
                    file_path=file_path,
                    line_number=if_node.body[0].lineno,
                )
    
    def _check_unused_definitions(self, tree: ast.AST, file_path: str) -> None:
        """
        Check for unused function and class definitions.
        
        Args:
            tree: The AST to analyze.
            file_path: Path to the file being analyzed.
        """
        # Collect all defined functions and classes
        defined_names = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined_names[node.name] = node
        
        # Collect all used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                if isinstance(node.value, ast.Name):
                    used_names.add(f"{node.value.id}.{node.attr}")
        
        # Check for unused definitions
        for name, node in defined_names.items():
            # Skip if it's a special method or likely to be used externally
            if (
                name.startswith("__")
                or name.startswith("test_")
                or name == "main"
            ):
                continue
            
            if name not in used_names:
                self.create_result(
                    message=f"Unused {'function' if isinstance(node, ast.FunctionDef) else 'class'} '{name}'",
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=RuleSeverity.INFO,
                )

