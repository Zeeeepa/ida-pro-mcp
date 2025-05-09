"""
Style analyzer for the PR static analysis system.

This module implements a style analyzer that checks code for formatting
and convention issues.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional, Pattern, Set, Tuple

from ida_pro_mcp.pr_analysis.core.analysis_engine import Analyzer, AnalyzerType
from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    CodeElement,
    CodeElementType,
    FileChange,
    Location,
)

logger = logging.getLogger(__name__)


class StyleAnalyzer(Analyzer):
    """Analyzer for detecting style issues in code."""

    def __init__(self, supported_languages: Optional[Set[str]] = None):
        """Initialize the style analyzer.

        Args:
            supported_languages: The programming languages supported by this analyzer.
                If None, all languages are supported.
        """
        super().__init__(
            name="StyleAnalyzer",
            description="Checks code for formatting and convention issues",
            analyzer_type=AnalyzerType.STYLE,
            supported_languages=supported_languages,
        )

    def analyze_file(self, file_change: FileChange) -> List[AnalysisResult]:
        """Analyze a file for style issues.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Skip deleted files
        if file_change.is_deleted or file_change.new_content is None:
            return results

        # Check for style issues based on the language
        if file_change.language == "python":
            results.extend(self._check_python_style(file_change))
        elif file_change.language in ["javascript", "typescript"]:
            results.extend(self._check_js_ts_style(file_change))
        # Add more language-specific style checks here

        return results

    def analyze_code_element(self, element: CodeElement) -> List[AnalysisResult]:
        """Analyze a code element for style issues.

        Args:
            element: The code element to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Check for style issues based on the element type and language
        if element.language == "python":
            if element.element_type in [CodeElementType.FUNCTION, CodeElementType.METHOD]:
                results.extend(self._check_python_function_style(element))
            elif element.element_type == CodeElementType.CLASS:
                results.extend(self._check_python_class_style(element))
        elif element.language in ["javascript", "typescript"]:
            if element.element_type in [CodeElementType.FUNCTION, CodeElementType.METHOD]:
                results.extend(self._check_js_ts_function_style(element))
            elif element.element_type == CodeElementType.CLASS:
                results.extend(self._check_js_ts_class_style(element))
        # Add more language-specific style checks here

        return results

    def _check_python_style(self, file_change: FileChange) -> List[AnalysisResult]:
        """Check Python code for style issues.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []
        if not file_change.new_content:
            return results

        # Check line length
        results.extend(self._check_line_length(file_change, max_length=88))

        # Check for trailing whitespace
        results.extend(self._check_trailing_whitespace(file_change))

        # Check for mixed tabs and spaces
        results.extend(self._check_mixed_tabs_spaces(file_change))

        return results

    def _check_js_ts_style(self, file_change: FileChange) -> List[AnalysisResult]:
        """Check JavaScript/TypeScript code for style issues.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []
        if not file_change.new_content:
            return results

        # Check line length
        results.extend(self._check_line_length(file_change, max_length=100))

        # Check for trailing whitespace
        results.extend(self._check_trailing_whitespace(file_change))

        # Check for mixed tabs and spaces
        results.extend(self._check_mixed_tabs_spaces(file_change))

        return results

    def _check_python_function_style(self, element: CodeElement) -> List[AnalysisResult]:
        """Check Python function for style issues.

        Args:
            element: The function element to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Check for snake_case naming convention
        if not self._is_snake_case(element.name):
            location = element.location
            result = AnalysisResult.from_location(
                result_type=AnalysisResultType.STYLE_ISSUE,
                severity=AnalysisResultSeverity.LOW,
                message=f"Function name '{element.name}' should use snake_case",
                location=location,
                code=element.name,
                analyzer_name=self.name,
                fix_suggestions=[f"Rename to '{self._to_snake_case(element.name)}'"],
            )
            results.append(result)

        return results

    def _check_python_class_style(self, element: CodeElement) -> List[AnalysisResult]:
        """Check Python class for style issues.

        Args:
            element: The class element to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Check for PascalCase naming convention
        if not self._is_pascal_case(element.name):
            location = element.location
            result = AnalysisResult.from_location(
                result_type=AnalysisResultType.STYLE_ISSUE,
                severity=AnalysisResultSeverity.LOW,
                message=f"Class name '{element.name}' should use PascalCase",
                location=location,
                code=element.name,
                analyzer_name=self.name,
                fix_suggestions=[f"Rename to '{self._to_pascal_case(element.name)}'"],
            )
            results.append(result)

        return results

    def _check_js_ts_function_style(self, element: CodeElement) -> List[AnalysisResult]:
        """Check JavaScript/TypeScript function for style issues.

        Args:
            element: The function element to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Check for camelCase naming convention
        if not self._is_camel_case(element.name):
            location = element.location
            result = AnalysisResult.from_location(
                result_type=AnalysisResultType.STYLE_ISSUE,
                severity=AnalysisResultSeverity.LOW,
                message=f"Function name '{element.name}' should use camelCase",
                location=location,
                code=element.name,
                analyzer_name=self.name,
                fix_suggestions=[f"Rename to '{self._to_camel_case(element.name)}'"],
            )
            results.append(result)

        return results

    def _check_js_ts_class_style(self, element: CodeElement) -> List[AnalysisResult]:
        """Check JavaScript/TypeScript class for style issues.

        Args:
            element: The class element to analyze.

        Returns:
            A list of analysis results.
        """
        results = []

        # Check for PascalCase naming convention
        if not self._is_pascal_case(element.name):
            location = element.location
            result = AnalysisResult.from_location(
                result_type=AnalysisResultType.STYLE_ISSUE,
                severity=AnalysisResultSeverity.LOW,
                message=f"Class name '{element.name}' should use PascalCase",
                location=location,
                code=element.name,
                analyzer_name=self.name,
                fix_suggestions=[f"Rename to '{self._to_pascal_case(element.name)}'"],
            )
            results.append(result)

        return results

    def _check_line_length(
        self, file_change: FileChange, max_length: int = 80
    ) -> List[AnalysisResult]:
        """Check for lines that exceed the maximum length.

        Args:
            file_change: The file change to analyze.
            max_length: The maximum allowed line length.

        Returns:
            A list of analysis results.
        """
        results = []
        if not file_change.new_content:
            return results

        lines = file_change.new_content.splitlines()
        for i, line in enumerate(lines):
            if len(line) > max_length:
                location = Location(
                    file_path=file_change.file_path,
                    line=i + 1,
                    column=max_length + 1,
                    end_line=i + 1,
                    end_column=len(line) + 1,
                )
                result = AnalysisResult.from_location(
                    result_type=AnalysisResultType.STYLE_ISSUE,
                    severity=AnalysisResultSeverity.LOW,
                    message=f"Line too long ({len(line)} > {max_length} characters)",
                    location=location,
                    code=line,
                    analyzer_name=self.name,
                )
                results.append(result)

        return results

    def _check_trailing_whitespace(self, file_change: FileChange) -> List[AnalysisResult]:
        """Check for lines with trailing whitespace.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []
        if not file_change.new_content:
            return results

        lines = file_change.new_content.splitlines()
        for i, line in enumerate(lines):
            if line and line[-1] in [" ", "\\t"]:
                location = Location(
                    file_path=file_change.file_path,
                    line=i + 1,
                    column=len(line),
                    end_line=i + 1,
                    end_column=len(line) + 1,
                )
                result = AnalysisResult.from_location(
                    result_type=AnalysisResultType.STYLE_ISSUE,
                    severity=AnalysisResultSeverity.LOW,
                    message="Line has trailing whitespace",
                    location=location,
                    code=line,
                    analyzer_name=self.name,
                    fix_suggestions=["Remove trailing whitespace"],
                )
                results.append(result)

        return results

    def _check_mixed_tabs_spaces(self, file_change: FileChange) -> List[AnalysisResult]:
        """Check for lines with mixed tabs and spaces for indentation.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        results = []
        if not file_change.new_content:
            return results

        lines = file_change.new_content.splitlines()
        for i, line in enumerate(lines):
            if re.search(r"^\t+ +|\t* +\t+", line):
                location = Location(
                    file_path=file_change.file_path,
                    line=i + 1,
                    column=1,
                    end_line=i + 1,
                    end_column=len(line) + 1,
                )
                result = AnalysisResult.from_location(
                    result_type=AnalysisResultType.STYLE_ISSUE,
                    severity=AnalysisResultSeverity.LOW,
                    message="Line has mixed tabs and spaces for indentation",
                    location=location,
                    code=line,
                    analyzer_name=self.name,
                    fix_suggestions=["Use consistent indentation (either tabs or spaces)"],
                )
                results.append(result)

        return results

    def _is_snake_case(self, name: str) -> bool:
        """Check if a name follows snake_case convention.

        Args:
            name: The name to check.

        Returns:
            True if the name follows snake_case convention, False otherwise.
        """
        return bool(re.match(r"^[a-z][a-z0-9_]*$", name))

    def _is_camel_case(self, name: str) -> bool:
        """Check if a name follows camelCase convention.

        Args:
            name: The name to check.

        Returns:
            True if the name follows camelCase convention, False otherwise.
        """
        return bool(re.match(r"^[a-z][a-zA-Z0-9]*$", name))

    def _is_pascal_case(self, name: str) -> bool:
        """Check if a name follows PascalCase convention.

        Args:
            name: The name to check.

        Returns:
            True if the name follows PascalCase convention, False otherwise.
        """
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case.

        Args:
            name: The name to convert.

        Returns:
            The name in snake_case.
        """
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _to_camel_case(self, name: str) -> str:
        """Convert a name to camelCase.

        Args:
            name: The name to convert.

        Returns:
            The name in camelCase.
        """
        s = re.sub(r"(_|-)+", " ", name).title().replace(" ", "")
        return s[0].lower() + s[1:]

    def _to_pascal_case(self, name: str) -> str:
        """Convert a name to PascalCase.

        Args:
            name: The name to convert.

        Returns:
            The name in PascalCase.
        """
        s = re.sub(r"(_|-)+", " ", name).title().replace(" ", "")
        return s

