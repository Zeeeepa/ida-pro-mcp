"""
Syntax analyzer for the PR static analysis system.

This module implements a syntax analyzer that uses the parser from graph-sitter
to detect syntax errors in code.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import List, Optional, Set

from ida_pro_mcp.pr_analysis.core.analysis_engine import Analyzer, AnalyzerType
from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    CodeElement,
    FileChange,
    Location,
)

logger = logging.getLogger(__name__)


class SyntaxAnalyzer(Analyzer):
    """Analyzer for detecting syntax errors in code."""

    def __init__(self, supported_languages: Optional[Set[str]] = None):
        """Initialize the syntax analyzer.

        Args:
            supported_languages: The programming languages supported by this analyzer.
                If None, all languages are supported.
        """
        super().__init__(
            name="SyntaxAnalyzer",
            description="Detects syntax errors in code using the parser from graph-sitter",
            analyzer_type=AnalyzerType.SYNTAX,
            supported_languages=supported_languages,
        )

    def analyze_file(self, file_change: FileChange) -> List[AnalysisResult]:
        """Analyze a file for syntax errors.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Skip deleted files
        if file_change.is_deleted or file_change.new_content is None:
            return results

        # Check for syntax errors based on the language
        if file_change.language == "python":
            results.extend(self._check_python_syntax(file_change))
        # Add more language-specific syntax checks here

        return results

    def analyze_code_element(self, element: CodeElement) -> List[AnalysisResult]:
        """Analyze a code element for syntax errors.

        Args:
            element: The code element to analyze.

        Returns:
            A list of analysis results.
        """
        # For syntax analysis, we typically analyze the entire file
        # So this method doesn't do much for this analyzer
        return []

    def _check_python_syntax(self, file_change: FileChange) -> List[AnalysisResult]:
        """Check Python code for syntax errors.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []
        if not file_change.new_content:
            return results

        try:
            # Try to parse the Python code
            ast.parse(file_change.new_content)
        except SyntaxError as e:
            # Create an analysis result for the syntax error
            location = Location(
                file_path=file_change.file_path,
                line=e.lineno,
                column=e.offset or 0,
                end_line=e.end_lineno,
                end_column=e.end_offset,
            )

            # Get the line of code with the error
            lines = file_change.new_content.splitlines()
            code = lines[e.lineno - 1] if e.lineno <= len(lines) else ""

            result = AnalysisResult.from_location(
                result_type=AnalysisResultType.SYNTAX_ERROR,
                severity=AnalysisResultSeverity.HIGH,
                message=f"Syntax error: {e.msg}",
                location=location,
                code=code,
                analyzer_name=self.name,
            )
            results.append(result)

        return results

