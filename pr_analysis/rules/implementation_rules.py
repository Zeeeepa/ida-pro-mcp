"""
Implementation rules for PR static analysis.

This module provides rules for checking code implementation.
"""

import ast
import re
from typing import List, ClassVar, Dict, Any, Set, Optional

from .base_rule import BaseRule
from ..core.analysis_context import PRAnalysisContext, AnalysisResult


class ComplexityRule(BaseRule):
    """Rule that checks for code complexity."""
    
    RULE_ID: ClassVar[str] = "implementation.complexity"
    RULE_NAME: ClassVar[str] = "Code Complexity"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for code with high cyclomatic complexity"
    RULE_CATEGORY: ClassVar[str] = "implementation"
    RULE_PRIORITY: ClassVar[int] = 4
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for code complexity.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        max_complexity = context.metadata.get("max_complexity", 15)
        
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
                            # Calculate complexity
                            complexity = self._calculate_complexity(node)
                            if complexity > max_complexity:
                                results.append(AnalysisResult(
                                    rule_id=self.RULE_ID,
                                    rule_name=self.RULE_NAME,
                                    severity="warning",
                                    message=f"Function '{node.name}' has a cyclomatic complexity of {complexity}, which exceeds the maximum of {max_complexity}",
                                    file=file_change.filename,
                                    line=node.lineno,
                                    suggested_fix="Consider refactoring this function into smaller, more focused functions",
                                    metadata={
                                        "function_name": node.name,
                                        "complexity": complexity,
                                        "max_complexity": max_complexity,
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
            
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate the cyclomatic complexity of a function.
        
        Args:
            node: The function definition node
            
        Returns:
            The cyclomatic complexity
        """
        # Start with a complexity of 1 (for the function itself)
        complexity = 1
        
        # Count branching statements
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.And):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.Or):
                complexity += len(child.values) - 1
                
        return complexity


class UnusedImportRule(BaseRule):
    """Rule that checks for unused imports."""
    
    RULE_ID: ClassVar[str] = "implementation.unused_import"
    RULE_NAME: ClassVar[str] = "Unused Import"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for unused imports in Python files"
    RULE_CATEGORY: ClassVar[str] = "implementation"
    RULE_PRIORITY: ClassVar[int] = 2
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for unused imports.
        
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
                    
                # Find all imports
                imports = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports[name.asname or name.name] = (node.lineno, name.name)
                    elif isinstance(node, ast.ImportFrom):
                        for name in node.names:
                            imports[name.asname or name.name] = (node.lineno, f"{node.module}.{name.name}")
                            
                # Find all names used in the file
                used_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        # Handle attributes like module.attribute
                        if isinstance(node.value, ast.Name):
                            used_names.add(node.value.id)
                            
                # Find unused imports
                for name, (lineno, import_name) in imports.items():
                    if name not in used_names and lineno in file_change.changed_lines:
                        results.append(AnalysisResult(
                            rule_id=self.RULE_ID,
                            rule_name=self.RULE_NAME,
                            severity="warning",
                            message=f"Unused import: {import_name}",
                            file=file_change.filename,
                            line=lineno,
                            suggested_fix=f"Remove the unused import",
                            metadata={
                                "import_name": import_name,
                            },
                        ))
            except SyntaxError:
                # Skip files with syntax errors
                continue
                
        return results


class DuplicateCodeRule(BaseRule):
    """Rule that checks for duplicate code."""
    
    RULE_ID: ClassVar[str] = "implementation.duplicate_code"
    RULE_NAME: ClassVar[str] = "Duplicate Code"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for duplicate code blocks"
    RULE_CATEGORY: ClassVar[str] = "implementation"
    RULE_PRIORITY: ClassVar[int] = 3
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for duplicate code.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        min_duplicate_lines = context.metadata.get("min_duplicate_lines", 5)
        
        # Group files by extension
        files_by_ext = {}
        for file_change in context.get_code_files():
            if file_change.status == "removed":
                continue
                
            # Skip files that are too large
            if file_change.patch and len(file_change.patch) > 1000000:  # 1MB
                continue
                
            ext = file_change.filename.split(".")[-1] if "." in file_change.filename else ""
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file_change)
            
        # Check for duplicates within each file type
        for ext, files in files_by_ext.items():
            # Skip if there's only one file
            if len(files) < 2:
                continue
                
            # Extract code blocks from each file
            code_blocks = {}
            for file_change in files:
                blocks = self._extract_code_blocks(file_change.patch, min_duplicate_lines)
                if blocks:
                    code_blocks[file_change.filename] = blocks
                    
            # Check for duplicates
            duplicates = self._find_duplicates(code_blocks)
            for dup in duplicates:
                # Only report duplicates if at least one of the files has changed lines
                if any(line in file_change.changed_lines for file_change in files for line in dup["lines"]):
                    results.append(AnalysisResult(
                        rule_id=self.RULE_ID,
                        rule_name=self.RULE_NAME,
                        severity="warning",
                        message=f"Duplicate code found in {len(dup['files'])} files",
                        file=dup["files"][0],
                        line=dup["lines"][0],
                        suggested_fix="Consider refactoring the duplicate code into a shared function or class",
                        metadata={
                            "files": dup["files"],
                            "lines": dup["lines"],
                            "code": dup["code"],
                        },
                    ))
                    
        return results
        
    def _extract_code_blocks(self, patch: str, min_lines: int) -> List[Dict[str, Any]]:
        """
        Extract code blocks from a patch.
        
        Args:
            patch: The patch text
            min_lines: The minimum number of lines for a block
            
        Returns:
            A list of code blocks
        """
        blocks = []
        
        # Extract added lines from the patch
        added_lines = []
        line_numbers = []
        
        current_line = 0
        in_hunk = False
        
        for line in patch.splitlines():
            # Check for hunk header
            if line.startswith("@@"):
                # Extract line numbers from hunk header
                match = re.match(r"^@@ -\d+,\d+ \+(\d+),\d+ @@", line)
                if match:
                    current_line = int(match.group(1))
                    in_hunk = True
                continue
                
            if not in_hunk:
                continue
                
            # Process lines in hunk
            if line.startswith("+") and not line.startswith("+++"):
                # Added line
                added_lines.append(line[1:])  # Remove the "+" prefix
                line_numbers.append(current_line)
                current_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                # Removed line - don't increment line number
                pass
            else:
                # Context line
                current_line += 1
                
        # Split into blocks of at least min_lines
        if len(added_lines) >= min_lines:
            for i in range(len(added_lines) - min_lines + 1):
                block = added_lines[i:i+min_lines]
                blocks.append({
                    "code": "\n".join(block),
                    "lines": line_numbers[i:i+min_lines],
                })
                
        return blocks
        
    def _find_duplicates(self, code_blocks: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Find duplicate code blocks.
        
        Args:
            code_blocks: A dictionary mapping filenames to code blocks
            
        Returns:
            A list of duplicate code blocks
        """
        duplicates = []
        
        # Create a map of code to files and lines
        code_map = {}
        for filename, blocks in code_blocks.items():
            for block in blocks:
                code = block["code"]
                if code not in code_map:
                    code_map[code] = {
                        "files": [],
                        "lines": [],
                        "code": code,
                    }
                code_map[code]["files"].append(filename)
                code_map[code]["lines"].append(block["lines"][0])
                
        # Find duplicates
        for code, info in code_map.items():
            if len(info["files"]) > 1:
                duplicates.append(info)
                
        return duplicates

