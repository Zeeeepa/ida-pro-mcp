"""
Base rule class for PR static analysis.

This module defines the base class for all analysis rules used in the PR static analysis system.
Rules are used to detect errors, issues, wrongly implemented features, and parameter problems
in pull requests.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class RuleCategory(Enum):
    """Categories of analysis rules."""
    CODE_INTEGRITY = auto()
    PARAMETER = auto()
    IMPLEMENTATION = auto()


class RuleSeverity(Enum):
    """Severity levels for rule results."""
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


class RuleResult:
    """Result of applying a rule to the analysis context."""

    def __init__(
        self,
        rule_id: str,
        message: str,
        file_path: str,
        line_number: int,
        severity: RuleSeverity,
        category: RuleCategory,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a rule result.

        Args:
            rule_id: Unique identifier of the rule that produced this result.
            message: Human-readable message describing the issue.
            file_path: Path to the file where the issue was found.
            line_number: Line number in the file where the issue was found.
            severity: Severity level of the issue.
            category: Category of the rule that produced this result.
            additional_data: Additional data related to the issue.
        """
        self.rule_id = rule_id
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.category = category
        self.additional_data = additional_data or {}

    def __str__(self) -> str:
        """Return a string representation of the rule result."""
        return f"{self.severity.name} in {self.file_path}:{self.line_number} - {self.message} ({self.rule_id})"


class BaseRule(ABC):
    """Base class for all analysis rules."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: RuleCategory,
        severity: RuleSeverity,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a rule.

        Args:
            rule_id: Unique identifier for the rule.
            name: Human-readable name for the rule.
            description: Detailed description of what the rule checks.
            category: Category of the rule.
            severity: Default severity level of issues found by the rule.
            config: Rule-specific configuration.
        """
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.config = config or {}
        self.results: List[RuleResult] = []

    @abstractmethod
    def apply(self, context: Any) -> List[RuleResult]:
        """
        Apply the rule to the analysis context.

        Args:
            context: The analysis context containing the data to analyze.

        Returns:
            A list of rule results.
        """
        pass

    def create_result(
        self,
        message: str,
        file_path: str,
        line_number: int,
        severity: Optional[RuleSeverity] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> RuleResult:
        """
        Create a result object for this rule.

        Args:
            message: Human-readable message describing the issue.
            file_path: Path to the file where the issue was found.
            line_number: Line number in the file where the issue was found.
            severity: Severity level of the issue. If None, uses the rule's default severity.
            additional_data: Additional data related to the issue.

        Returns:
            A RuleResult object.
        """
        severity = severity or self.severity
        result = RuleResult(
            rule_id=self.rule_id,
            message=message,
            file_path=file_path,
            line_number=line_number,
            severity=severity,
            category=self.category,
            additional_data=additional_data
        )
        self.results.append(result)
        return result

    def is_applicable(self, context: Any) -> bool:
        """
        Check if the rule is applicable to the current context.

        Args:
            context: The analysis context containing the data to analyze.

        Returns:
            True if the rule is applicable, False otherwise.
        """
        return True

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get rule-specific configuration.

        Returns:
            A dictionary containing the rule's configuration.
        """
        return self.config

    def set_configuration(self, config: Dict[str, Any]) -> None:
        """
        Set rule-specific configuration.

        Args:
            config: A dictionary containing the rule's configuration.
        """
        self.config = config

    def get_results(self) -> List[RuleResult]:
        """
        Get all results produced by this rule.

        Returns:
            A list of rule results.
        """
        return self.results

    def clear_results(self) -> None:
        """Clear all results produced by this rule."""
        self.results = []

