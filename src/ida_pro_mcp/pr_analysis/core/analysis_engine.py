"""
Core Analysis Engine for PR Static Analysis.

This module implements the core analysis engine for the PR static analysis system.
The analysis engine is responsible for analyzing code changes in pull requests
and identifying potential issues.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    CodeElement,
    FileChange,
)

logger = logging.getLogger(__name__)


class AnalyzerType(Enum):
    """Types of analyzers supported by the analysis engine."""

    SYNTAX = auto()
    SEMANTIC = auto()
    STYLE = auto()
    PERFORMANCE = auto()
    SECURITY = auto()
    CUSTOM = auto()


class Analyzer(ABC):
    """Base class for all analyzers."""

    analyzer_type: AnalyzerType
    name: str
    description: str
    supported_languages: Set[str]

    def __init__(
        self,
        name: str,
        description: str,
        analyzer_type: AnalyzerType,
        supported_languages: Optional[Set[str]] = None,
    ):
        """Initialize the analyzer.

        Args:
            name: The name of the analyzer.
            description: A description of what the analyzer does.
            analyzer_type: The type of analyzer.
            supported_languages: The programming languages supported by this analyzer.
                If None, all languages are supported.
        """
        self.name = name
        self.description = description
        self.analyzer_type = analyzer_type
        self.supported_languages = supported_languages or set()

    def supports_language(self, language: str) -> bool:
        """Check if the analyzer supports the given language.

        Args:
            language: The programming language to check.

        Returns:
            True if the analyzer supports the language, False otherwise.
        """
        return not self.supported_languages or language in self.supported_languages

    @abstractmethod
    def analyze_file(self, file_change: FileChange) -> List[AnalysisResult]:
        """Analyze a file and return a list of analysis results.

        Args:
            file_change: The file change to analyze.

        Returns:
            A list of analysis results.
        """
        pass

    @abstractmethod
    def analyze_code_element(self, element: CodeElement) -> List[AnalysisResult]:
        """Analyze a code element and return a list of analysis results.

        Args:
            element: The code element to analyze.

        Returns:
            A list of analysis results.
        """
        pass


class AnalysisPipeline:
    """A pipeline for processing PR changes through multiple analyzers."""

    def __init__(self, analyzers: Optional[List[Analyzer]] = None):
        """Initialize the analysis pipeline.

        Args:
            analyzers: A list of analyzers to use in the pipeline.
        """
        self.analyzers = analyzers or []

    def add_analyzer(self, analyzer: Analyzer) -> None:
        """Add an analyzer to the pipeline.

        Args:
            analyzer: The analyzer to add.
        """
        self.analyzers.append(analyzer)

    def remove_analyzer(self, analyzer_name: str) -> bool:
        """Remove an analyzer from the pipeline by name.

        Args:
            analyzer_name: The name of the analyzer to remove.

        Returns:
            True if the analyzer was removed, False otherwise.
        """
        for i, analyzer in enumerate(self.analyzers):
            if analyzer.name == analyzer_name:
                self.analyzers.pop(i)
                return True
        return False

    def process_file(self, file_change: FileChange) -> List[AnalysisResult]:
        """Process a file through all analyzers in the pipeline.

        Args:
            file_change: The file change to process.

        Returns:
            A list of analysis results from all analyzers.
        """
        results = []
        for analyzer in self.analyzers:
            if analyzer.supports_language(file_change.language):
                try:
                    analyzer_results = analyzer.analyze_file(file_change)
                    results.extend(analyzer_results)
                except Exception as e:
                    logger.error(f"Error in analyzer {analyzer.name}: {e}")
        return results

    def process_code_element(self, element: CodeElement) -> List[AnalysisResult]:
        """Process a code element through all analyzers in the pipeline.

        Args:
            element: The code element to process.

        Returns:
            A list of analysis results from all analyzers.
        """
        results = []
        for analyzer in self.analyzers:
            if analyzer.supports_language(element.language):
                try:
                    analyzer_results = analyzer.analyze_code_element(element)
                    results.extend(analyzer_results)
                except Exception as e:
                    logger.error(f"Error in analyzer {analyzer.name}: {e}")
        return results


class AnalysisEngine:
    """The core analysis engine for PR static analysis.

    This class coordinates different analyzers and provides methods for
    analyzing files, functions, classes, and other code elements.
    """

    def __init__(self):
        """Initialize the analysis engine."""
        self.pipelines: Dict[str, AnalysisPipeline] = {}
        self.default_pipeline = AnalysisPipeline()
        self.analyzers: Dict[str, Analyzer] = {}

    def register_analyzer(self, analyzer: Analyzer) -> None:
        """Register an analyzer with the engine.

        Args:
            analyzer: The analyzer to register.
        """
        self.analyzers[analyzer.name] = analyzer
        self.default_pipeline.add_analyzer(analyzer)

    def create_pipeline(self, name: str, analyzers: List[str]) -> AnalysisPipeline:
        """Create a new analysis pipeline with the specified analyzers.

        Args:
            name: The name of the pipeline.
            analyzers: A list of analyzer names to include in the pipeline.

        Returns:
            The created pipeline.

        Raises:
            ValueError: If an analyzer name is not registered.
        """
        pipeline = AnalysisPipeline()
        for analyzer_name in analyzers:
            if analyzer_name not in self.analyzers:
                raise ValueError(f"Analyzer {analyzer_name} is not registered")
            pipeline.add_analyzer(self.analyzers[analyzer_name])
        self.pipelines[name] = pipeline
        return pipeline

    def get_pipeline(self, name: str) -> AnalysisPipeline:
        """Get a pipeline by name.

        Args:
            name: The name of the pipeline.

        Returns:
            The pipeline.

        Raises:
            ValueError: If the pipeline does not exist.
        """
        if name not in self.pipelines:
            raise ValueError(f"Pipeline {name} does not exist")
        return self.pipelines[name]

    def analyze_file(
        self, file_change: FileChange, pipeline_name: Optional[str] = None
    ) -> List[AnalysisResult]:
        """Analyze a file using the specified pipeline.

        Args:
            file_change: The file change to analyze.
            pipeline_name: The name of the pipeline to use. If None, the default pipeline is used.

        Returns:
            A list of analysis results.
        """
        pipeline = (
            self.get_pipeline(pipeline_name) if pipeline_name else self.default_pipeline
        )
        return pipeline.process_file(file_change)

    def analyze_code_element(
        self, element: CodeElement, pipeline_name: Optional[str] = None
    ) -> List[AnalysisResult]:
        """Analyze a code element using the specified pipeline.

        Args:
            element: The code element to analyze.
            pipeline_name: The name of the pipeline to use. If None, the default pipeline is used.

        Returns:
            A list of analysis results.
        """
        pipeline = (
            self.get_pipeline(pipeline_name) if pipeline_name else self.default_pipeline
        )
        return pipeline.process_code_element(element)

    def analyze_pr_changes(
        self, file_changes: List[FileChange], pipeline_name: Optional[str] = None
    ) -> Dict[Path, List[AnalysisResult]]:
        """Analyze all changes in a PR using the specified pipeline.

        Args:
            file_changes: The file changes to analyze.
            pipeline_name: The name of the pipeline to use. If None, the default pipeline is used.

        Returns:
            A dictionary mapping file paths to lists of analysis results.
        """
        results: Dict[Path, List[AnalysisResult]] = {}
        for file_change in file_changes:
            file_results = self.analyze_file(file_change, pipeline_name)
            if file_results:
                results[file_change.file_path] = file_results
        return results

    def filter_results(
        self,
        results: List[AnalysisResult],
        severity: Optional[AnalysisResultSeverity] = None,
        result_type: Optional[AnalysisResultType] = None,
    ) -> List[AnalysisResult]:
        """Filter analysis results by severity and/or type.

        Args:
            results: The results to filter.
            severity: The minimum severity level to include.
            result_type: The type of results to include.

        Returns:
            The filtered results.
        """
        filtered_results = results
        if severity:
            filtered_results = [r for r in filtered_results if r.severity >= severity]
        if result_type:
            filtered_results = [r for r in filtered_results if r.result_type == result_type]
        return filtered_results

    def sort_results(
        self, results: List[AnalysisResult], by_severity: bool = True
    ) -> List[AnalysisResult]:
        """Sort analysis results.

        Args:
            results: The results to sort.
            by_severity: If True, sort by severity (highest first).
                Otherwise, sort by location.

        Returns:
            The sorted results.
        """
        if by_severity:
            return sorted(results, key=lambda r: r.severity, reverse=True)
        return sorted(results, key=lambda r: (r.file_path, r.line, r.column))

