"""
Models for the PR static analysis system.

This module defines the data models used by the PR static analysis system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class AnalysisResultType(Enum):
    """Types of analysis results."""

    SYNTAX_ERROR = auto()
    SEMANTIC_ERROR = auto()
    STYLE_ISSUE = auto()
    PERFORMANCE_ISSUE = auto()
    SECURITY_VULNERABILITY = auto()
    BEST_PRACTICE = auto()
    SUGGESTION = auto()
    INFORMATION = auto()


class AnalysisResultSeverity(IntEnum):
    """Severity levels for analysis results."""

    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class CodeElementType(Enum):
    """Types of code elements."""

    FILE = auto()
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    VARIABLE = auto()
    IMPORT = auto()
    STATEMENT = auto()
    EXPRESSION = auto()
    COMMENT = auto()
    OTHER = auto()


@dataclass
class Location:
    """A location in a file."""

    file_path: Path
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass
class CodeElement:
    """A code element in a file."""

    element_type: CodeElementType
    name: str
    location: Location
    language: str
    content: str
    parent: Optional[CodeElement] = None
    children: List[CodeElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileChange:
    """A change to a file in a PR."""

    file_path: Path
    language: str
    old_content: Optional[str]
    new_content: Optional[str]
    is_new: bool = False
    is_deleted: bool = False
    is_renamed: bool = False
    old_file_path: Optional[Path] = None
    diff: Optional[str] = None
    elements: List[CodeElement] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """A result from analyzing a code element."""

    result_type: AnalysisResultType
    severity: AnalysisResultSeverity
    message: str
    file_path: Path
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    code: Optional[str] = None
    analyzer_name: str = ""
    fix_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_location(
        cls,
        result_type: AnalysisResultType,
        severity: AnalysisResultSeverity,
        message: str,
        location: Location,
        code: Optional[str] = None,
        analyzer_name: str = "",
        fix_suggestions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AnalysisResult:
        """Create an analysis result from a location.

        Args:
            result_type: The type of the result.
            severity: The severity of the result.
            message: The message describing the result.
            location: The location of the result.
            code: The code snippet related to the result.
            analyzer_name: The name of the analyzer that produced the result.
            fix_suggestions: Suggestions for fixing the issue.
            metadata: Additional metadata for the result.

        Returns:
            An analysis result.
        """
        return cls(
            result_type=result_type,
            severity=severity,
            message=message,
            file_path=location.file_path,
            line=location.line,
            column=location.column,
            end_line=location.end_line,
            end_column=location.end_column,
            code=code,
            analyzer_name=analyzer_name,
            fix_suggestions=fix_suggestions or [],
            metadata=metadata or {},
        )


@dataclass
class AnalysisContext:
    """Context for an analysis operation."""

    file_changes: List[FileChange]
    repository_path: Path
    base_commit: str
    head_commit: str
    metadata: Dict[str, Any] = field(default_factory=dict)

