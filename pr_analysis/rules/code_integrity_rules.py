"""
Code integrity rules for PR static analysis.

This module provides rules for checking code integrity.
"""

import os
from typing import List, ClassVar

from .base_rule import BaseRule
from ..core.analysis_context import PRAnalysisContext, AnalysisResult


class LineLength(BaseRule):
    """Rule that checks for lines exceeding the maximum length."""
    
    RULE_ID: ClassVar[str] = "code_integrity.line_length"
    RULE_NAME: ClassVar[str] = "Line Length"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for lines exceeding the maximum length"
    RULE_CATEGORY: ClassVar[str] = "code_integrity"
    RULE_PRIORITY: ClassVar[int] = 5
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for lines exceeding the maximum length.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        max_line_length = context.metadata.get("max_line_length", 120)
        
        for file_change in context.get_code_files():
            if file_change.status == "removed":
                continue
                
            # Skip files that are too large
            if file_change.patch and len(file_change.patch) > 1000000:  # 1MB
                continue
                
            if not file_change.patch:
                continue
                
            # Check each changed line
            for line_num in file_change.changed_lines:
                # Extract the line from the patch
                line = self._get_line_from_patch(file_change.patch, line_num)
                if line and len(line) > max_line_length:
                    results.append(AnalysisResult(
                        rule_id=self.RULE_ID,
                        rule_name=self.RULE_NAME,
                        severity="warning",
                        message=f"Line exceeds maximum length of {max_line_length} characters",
                        file=file_change.filename,
                        line=line_num,
                        suggested_fix=f"Consider breaking this line into multiple lines",
                        metadata={
                            "line_length": len(line),
                            "max_length": max_line_length,
                        },
                    ))
                    
        return results
        
    def _get_line_from_patch(self, patch: str, line_num: int) -> str:
        """
        Extract a line from a patch.
        
        Args:
            patch: The patch text
            line_num: The line number to extract
            
        Returns:
            The line text, or an empty string if not found
        """
        import re
        
        # Find the hunk that contains the line
        hunk_header_re = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")
        
        current_line = 0
        in_hunk = False
        
        for patch_line in patch.splitlines():
            # Check for hunk header
            hunk_match = hunk_header_re.match(patch_line)
            if hunk_match:
                # Extract line numbers from hunk header
                current_line = int(hunk_match.group(3))
                in_hunk = True
                continue
                
            if not in_hunk:
                continue
                
            # Process lines in hunk
            if patch_line.startswith("+") and not patch_line.startswith("+++"):
                # Added line
                if current_line == line_num:
                    return patch_line[1:]  # Remove the "+" prefix
                current_line += 1
            elif patch_line.startswith("-") and not patch_line.startswith("---"):
                # Removed line - don't increment line number
                pass
            else:
                # Context line
                if current_line == line_num:
                    return patch_line[1:] if patch_line.startswith(" ") else patch_line
                current_line += 1
                
        return ""


class FileSize(BaseRule):
    """Rule that checks for files exceeding the maximum size."""
    
    RULE_ID: ClassVar[str] = "code_integrity.file_size"
    RULE_NAME: ClassVar[str] = "File Size"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for files exceeding the maximum size"
    RULE_CATEGORY: ClassVar[str] = "code_integrity"
    RULE_PRIORITY: ClassVar[int] = 5
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for files exceeding the maximum size.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        max_file_size = context.metadata.get("max_file_size", 1000000)  # 1MB
        
        for file_change in context.get_code_files():
            if file_change.status == "removed":
                continue
                
            # Check file size from patch
            if file_change.patch:
                patch_size = len(file_change.patch)
                if patch_size > max_file_size:
                    results.append(AnalysisResult(
                        rule_id=self.RULE_ID,
                        rule_name=self.RULE_NAME,
                        severity="warning",
                        message=f"File exceeds maximum size of {max_file_size // 1024} KB",
                        file=file_change.filename,
                        suggested_fix=f"Consider breaking this file into multiple smaller files",
                        metadata={
                            "file_size": patch_size,
                            "max_size": max_file_size,
                        },
                    ))
                    
        return results


class FileNaming(BaseRule):
    """Rule that checks for proper file naming conventions."""
    
    RULE_ID: ClassVar[str] = "code_integrity.file_naming"
    RULE_NAME: ClassVar[str] = "File Naming"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for proper file naming conventions"
    RULE_CATEGORY: ClassVar[str] = "code_integrity"
    RULE_PRIORITY: ClassVar[int] = 3
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for proper file naming conventions.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        
        for file_change in context.file_changes.values():
            if file_change.status == "removed":
                continue
                
            filename = file_change.filename
            basename = os.path.basename(filename)
            
            # Check for snake_case in Python files
            if filename.endswith(".py") and not self._is_snake_case(basename):
                results.append(AnalysisResult(
                    rule_id=self.RULE_ID,
                    rule_name=self.RULE_NAME,
                    severity="warning",
                    message=f"Python file names should use snake_case",
                    file=filename,
                    suggested_fix=f"Rename to {self._to_snake_case(basename)}",
                    metadata={
                        "current_name": basename,
                        "suggested_name": self._to_snake_case(basename),
                    },
                ))
                
            # Check for camelCase or PascalCase in JavaScript/TypeScript files
            if filename.endswith((".js", ".ts", ".jsx", ".tsx")) and not self._is_camel_or_pascal_case(basename):
                results.append(AnalysisResult(
                    rule_id=self.RULE_ID,
                    rule_name=self.RULE_NAME,
                    severity="warning",
                    message=f"JavaScript/TypeScript file names should use camelCase or PascalCase",
                    file=filename,
                    suggested_fix=f"Rename to {self._to_camel_case(basename)}",
                    metadata={
                        "current_name": basename,
                        "suggested_name": self._to_camel_case(basename),
                    },
                ))
                
        return results
        
    def _is_snake_case(self, name: str) -> bool:
        """
        Check if a name is in snake_case.
        
        Args:
            name: The name to check
            
        Returns:
            True if the name is in snake_case, False otherwise
        """
        import re
        name = os.path.splitext(name)[0]  # Remove extension
        return bool(re.match(r"^[a-z][a-z0-9_]*$", name))
        
    def _is_camel_or_pascal_case(self, name: str) -> bool:
        """
        Check if a name is in camelCase or PascalCase.
        
        Args:
            name: The name to check
            
        Returns:
            True if the name is in camelCase or PascalCase, False otherwise
        """
        import re
        name = os.path.splitext(name)[0]  # Remove extension
        return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", name) and "_" not in name)
        
    def _to_snake_case(self, name: str) -> str:
        """
        Convert a name to snake_case.
        
        Args:
            name: The name to convert
            
        Returns:
            The name in snake_case
        """
        import re
        name = os.path.splitext(name)[0]  # Remove extension
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower() + os.path.splitext(name)[1]  # Add extension back
        
    def _to_camel_case(self, name: str) -> str:
        """
        Convert a name to camelCase.
        
        Args:
            name: The name to convert
            
        Returns:
            The name in camelCase
        """
        import re
        name = os.path.splitext(name)[0]  # Remove extension
        components = name.split("_")
        return components[0].lower() + "".join(x.title() for x in components[1:]) + os.path.splitext(name)[1]  # Add extension back

