"""
Code integrity rules for the PR static analysis system.

This module contains rules for detecting code quality issues, such as
unused parameters, high complexity, and duplicate code.
"""
import re
from typing import List, Dict, Any, Optional

from ..core import BaseRule, AnalysisResult, AnalysisContext


class UnusedParameterRule(BaseRule):
    """
    Rule for detecting unused parameters in functions.
    """
    def __init__(self):
        """Initialize the unused parameter rule."""
        super().__init__(
            name="unused_parameter",
            description="Detects unused parameters in functions",
            severity="warning"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect unused parameters in functions.

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
            
            # Simple regex to find function definitions
            # This is a simplified approach and might not catch all cases
            function_pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
            for match in re.finditer(function_pattern, content):
                func_name = match.group(1)
                params_str = match.group(2)
                
                # Skip if there are no parameters
                if not params_str.strip():
                    continue
                
                # Extract parameter names
                params = []
                for param in params_str.split(','):
                    param = param.strip()
                    if not param:
                        continue
                    
                    # Handle default values and type annotations
                    param_name = param.split('=')[0].split(':')[0].strip()
                    
                    # Skip self, cls, and *args, **kwargs
                    if param_name in ('self', 'cls') or param_name.startswith('*'):
                        continue
                        
                    params.append(param_name)
                
                # Find the function body
                # This is a simplified approach and might not work for all cases
                start_pos = match.end()
                indent_level = 0
                for i, char in enumerate(content[start_pos:]):
                    if char == '\n':
                        next_line_start = start_pos + i + 1
                        if next_line_start < len(content):
                            next_line = content[next_line_start:].split('\n')[0]
                            if next_line.strip() and not next_line.strip().startswith('#'):
                                indent = len(next_line) - len(next_line.lstrip())
                                if indent_level == 0:
                                    indent_level = indent
                                elif indent < indent_level:
                                    # End of function body
                                    break
                
                # Check if each parameter is used in the function body
                for param in params:
                    # This is a simplified check and might produce false positives/negatives
                    if param not in content[start_pos:start_pos + i]:
                        # Calculate line number
                        line_number = content[:match.start()].count('\n') + 1
                        
                        results.append(AnalysisResult(
                            rule_name=self.name,
                            message=f"Parameter '{param}' is not used in function '{func_name}'",
                            file_path=file_path,
                            line_number=line_number,
                            severity=self.severity
                        ))
        
        return results


class ComplexityRule(BaseRule):
    """
    Rule for detecting functions with high cyclomatic complexity.
    """
    def __init__(self, max_complexity: int = 10):
        """
        Initialize the complexity rule.
        
        Args:
            max_complexity: Maximum allowed cyclomatic complexity
        """
        super().__init__(
            name="high_complexity",
            description=f"Detects functions with cyclomatic complexity higher than {max_complexity}",
            severity="warning"
        )
        self.max_complexity = max_complexity

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect functions with high cyclomatic complexity.

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
            
            # Simple regex to find function definitions
            function_pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
            for match in re.finditer(function_pattern, content):
                func_name = match.group(1)
                
                # Find the function body
                start_pos = match.end()
                indent_level = 0
                for i, char in enumerate(content[start_pos:]):
                    if char == '\n':
                        next_line_start = start_pos + i + 1
                        if next_line_start < len(content):
                            next_line = content[next_line_start:].split('\n')[0]
                            if next_line.strip() and not next_line.strip().startswith('#'):
                                indent = len(next_line) - len(next_line.lstrip())
                                if indent_level == 0:
                                    indent_level = indent
                                elif indent < indent_level:
                                    # End of function body
                                    break
                
                # Calculate complexity based on control flow statements
                # This is a simplified approach and might not be accurate for all cases
                function_body = content[start_pos:start_pos + i]
                complexity = 1  # Base complexity
                
                # Count control flow statements
                complexity += function_body.count('if ')
                complexity += function_body.count('elif ')
                complexity += function_body.count('for ')
                complexity += function_body.count('while ')
                complexity += function_body.count('except')
                complexity += function_body.count('with ')
                complexity += function_body.count(' and ')
                complexity += function_body.count(' or ')
                
                if complexity > self.max_complexity:
                    # Calculate line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Function '{func_name}' has a cyclomatic complexity of {complexity}, which exceeds the maximum allowed value of {self.max_complexity}",
                        file_path=file_path,
                        line_number=line_number,
                        severity=self.severity,
                        additional_info={"complexity": complexity}
                    ))
        
        return results


class DuplicateCodeRule(BaseRule):
    """
    Rule for detecting duplicate code blocks.
    """
    def __init__(self, min_lines: int = 5):
        """
        Initialize the duplicate code rule.
        
        Args:
            min_lines: Minimum number of lines to consider as a duplicate block
        """
        super().__init__(
            name="duplicate_code",
            description=f"Detects duplicate code blocks of at least {min_lines} lines",
            severity="warning"
        )
        self.min_lines = min_lines

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect duplicate code blocks.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        # Get all changed files
        changed_files = context.get_changed_files()
        
        # Skip if there are no changed files
        if not changed_files:
            return results
        
        # Extract content from all changed files
        file_contents = {}
        for file_path in changed_files:
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            file_contents[file_path] = content
        
        # Skip if there are no Python files
        if not file_contents:
            return results
        
        # Find duplicate code blocks
        # This is a simplified approach and might not be efficient for large codebases
        for file_path, content in file_contents.items():
            lines = content.split('\n')
            
            for i in range(len(lines) - self.min_lines + 1):
                block = '\n'.join(lines[i:i + self.min_lines])
                
                # Skip empty or whitespace-only blocks
                if not block.strip():
                    continue
                
                # Check if this block appears elsewhere
                for other_file_path, other_content in file_contents.items():
                    # Skip the same file
                    if other_file_path == file_path:
                        continue
                        
                    other_lines = other_content.split('\n')
                    
                    for j in range(len(other_lines) - self.min_lines + 1):
                        other_block = '\n'.join(other_lines[j:j + self.min_lines])
                        
                        if block == other_block:
                            results.append(AnalysisResult(
                                rule_name=self.name,
                                message=f"Duplicate code block found in {other_file_path} at line {j + 1}",
                                file_path=file_path,
                                line_number=i + 1,
                                severity=self.severity,
                                additional_info={
                                    "duplicate_file": other_file_path,
                                    "duplicate_line": j + 1,
                                    "block": block
                                }
                            ))
        
        return results

