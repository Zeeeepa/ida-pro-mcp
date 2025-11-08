"""
Base rule definition for the PR static analysis system.

This module defines the BaseRule class which serves as the foundation
for all analysis rules in the system.
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class AnalysisResult:
    """
    Represents the result of a rule analysis.
    """
    def __init__(
        self,
        rule_name: str,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        severity: str = "warning",
        additional_info: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an analysis result.

        Args:
            rule_name: Name of the rule that produced this result
            message: Description of the issue found
            file_path: Path to the file where the issue was found
            line_number: Line number where the issue was found
            severity: Severity level of the issue (info, warning, error)
            additional_info: Any additional information about the issue
        """
        self.rule_name = rule_name
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.additional_info = additional_info or {}

    def __str__(self) -> str:
        """String representation of the analysis result."""
        location = ""
        if self.file_path:
            location = f"in {self.file_path}"
            if self.line_number is not None:
                location += f" at line {self.line_number}"
        
        return f"[{self.severity.upper()}] {self.rule_name}: {self.message} {location}"


class AnalysisContext:
    """
    Provides context for rule execution, including access to the PR data,
    changed files, and other relevant information.
    
    This is a placeholder implementation that will be replaced with the actual
    implementation when the core analysis engine components are developed.
    """
    def __init__(self, pr_data: Dict[str, Any] = None):
        """
        Initialize the analysis context.

        Args:
            pr_data: Data about the PR being analyzed
        """
        self.pr_data = pr_data or {}
        self._changed_files = []

    def get_changed_files(self) -> List[str]:
        """
        Get the list of files changed in the PR.

        Returns:
            List of file paths that were changed in the PR
        """
        return self._changed_files

    def get_file_content(self, file_path: str) -> str:
        """
        Get the content of a file.

        Args:
            file_path: Path to the file

        Returns:
            Content of the file as a string
        """
        # This is a placeholder implementation
        return ""

    def get_file_diff(self, file_path: str) -> str:
        """
        Get the diff for a file.

        Args:
            file_path: Path to the file

        Returns:
            Diff of the file as a string
        """
        # This is a placeholder implementation
        return ""


class BaseRule(ABC):
    """
    Base class for all analysis rules.
    
    This class defines the interface that all rules must implement and provides
    common functionality for rule execution.
    """
    def __init__(self, name: str, description: str, severity: str = "warning"):
        """
        Initialize a rule.

        Args:
            name: Unique identifier for the rule
            description: Human-readable description of what the rule checks for
            severity: Default severity level for issues found by this rule
        """
        self.name = name
        self.description = description
        self.severity = severity

    def should_run(self, context: AnalysisContext) -> bool:
        """
        Determine if the rule should run based on the context.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            True if the rule should run, False otherwise
        """
        # By default, all rules run on all PRs
        return True

    @abstractmethod
    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule and return results.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        raise NotImplementedError("Subclasses must implement run()")

    def __str__(self) -> str:
        """String representation of the rule."""
        return f"{self.name}: {self.description} (severity: {self.severity})"

