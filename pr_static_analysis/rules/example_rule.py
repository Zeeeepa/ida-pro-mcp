"""
Example Rule Module

This module provides an example rule for the PR static analysis system.
"""
from typing import List

from .base_rule import BaseRule
from ..core.analysis_context import PRAnalysisContext, AnalysisResult

class FileExtensionRule(BaseRule):
    """
    Example rule that checks file extensions.
    
    This rule checks if any files with specific extensions were changed in the PR.
    """
    
    RULE_ID = "file_extension_check"
    CATEGORY = "example"
    DESCRIPTION = "Checks if files with specific extensions were changed"
    SEVERITY = "info"
    
    def __init__(self, extensions=None):
        """
        Initialize the rule.
        
        Args:
            extensions: List of file extensions to check for.
        """
        super().__init__()
        self.extensions = extensions or [".py", ".js", ".ts"]
        
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze the PR and return results.
        
        Args:
            context: The PR analysis context.
            
        Returns:
            A list of analysis results.
        """
        results = []
        
        # Check each changed file
        for file_path in context.pr_data.files_changed:
            for ext in self.extensions:
                if file_path.endswith(ext):
                    results.append(AnalysisResult(
                        rule_id=self.RULE_ID,
                        status="pass",
                        message=f"Found {ext} file: {file_path}",
                        file_path=file_path,
                        details={"extension": ext}
                    ))
                    break
                    
        # If no files with the specified extensions were found, add a "fail" result
        if not results:
            results.append(AnalysisResult(
                rule_id=self.RULE_ID,
                status="fail",
                message=f"No files with extensions {', '.join(self.extensions)} were found",
                details={"checked_extensions": self.extensions}
            ))
            
        return results

class LineCountRule(BaseRule):
    """
    Example rule that checks line counts in files.
    
    This rule checks if any files exceed a specified line count threshold.
    """
    
    RULE_ID = "line_count_check"
    CATEGORY = "example"
    DESCRIPTION = "Checks if files exceed a specified line count threshold"
    SEVERITY = "warning"
    
    def __init__(self, threshold=100):
        """
        Initialize the rule.
        
        Args:
            threshold: The line count threshold.
        """
        super().__init__()
        self.threshold = threshold
        
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze the PR and return results.
        
        Args:
            context: The PR analysis context.
            
        Returns:
            A list of analysis results.
        """
        results = []
        
        # Check each changed file
        for file_path in context.pr_data.files_changed:
            # Get the content of the file in the head branch
            content = context.get_file_content_head(file_path)
            if content is None:
                # File was deleted or doesn't exist
                continue
                
            # Count the lines
            line_count = len(content.splitlines())
            
            if line_count > self.threshold:
                results.append(AnalysisResult(
                    rule_id=self.RULE_ID,
                    status="fail",
                    message=f"File {file_path} exceeds the line count threshold ({line_count} > {self.threshold})",
                    file_path=file_path,
                    details={
                        "line_count": line_count,
                        "threshold": self.threshold
                    }
                ))
            else:
                results.append(AnalysisResult(
                    rule_id=self.RULE_ID,
                    status="pass",
                    message=f"File {file_path} is within the line count threshold ({line_count} <= {self.threshold})",
                    file_path=file_path,
                    details={
                        "line_count": line_count,
                        "threshold": self.threshold
                    }
                ))
                
        return results

