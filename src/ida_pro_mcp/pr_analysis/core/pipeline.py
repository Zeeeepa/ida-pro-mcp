"""
Analysis pipeline for the PR static analysis system.

This module implements the analysis pipeline that processes PR changes in stages.
"""

from __future__ import annotations

import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from ida_pro_mcp.pr_analysis.core.analysis_engine import AnalysisEngine
from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisContext,
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    FileChange,
)

logger = logging.getLogger(__name__)


class AnalysisPipelineStage:
    """A stage in the analysis pipeline."""

    def __init__(self, name: str, description: str):
        """Initialize the pipeline stage.

        Args:
            name: The name of the stage.
            description: A description of what the stage does.
        """
        self.name = name
        self.description = description

    def process(
        self, context: AnalysisContext, engine: AnalysisEngine
    ) -> Dict[Path, List[AnalysisResult]]:
        """Process the analysis context and return results.

        Args:
            context: The analysis context.
            engine: The analysis engine.

        Returns:
            A dictionary mapping file paths to lists of analysis results.
        """
        raise NotImplementedError("Subclasses must implement this method")


class FileAnalysisStage(AnalysisPipelineStage):
    """A stage that analyzes individual files."""

    def __init__(
        self,
        name: str = "File Analysis",
        description: str = "Analyzes individual files for issues",
        pipeline_name: Optional[str] = None,
        parallel: bool = True,
    ):
        """Initialize the file analysis stage.

        Args:
            name: The name of the stage.
            description: A description of what the stage does.
            pipeline_name: The name of the pipeline to use for analysis.
            parallel: Whether to analyze files in parallel.
        """
        super().__init__(name, description)
        self.pipeline_name = pipeline_name
        self.parallel = parallel

    def process(
        self, context: AnalysisContext, engine: AnalysisEngine
    ) -> Dict[Path, List[AnalysisResult]]:
        """Process the analysis context and return results.

        Args:
            context: The analysis context.
            engine: The analysis engine.

        Returns:
            A dictionary mapping file paths to lists of analysis results.
        """
        if not self.parallel:
            return engine.analyze_pr_changes(context.file_changes, self.pipeline_name)

        # Analyze files in parallel
        results: Dict[Path, List[AnalysisResult]] = {}
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            future_to_file = {
                executor.submit(
                    engine.analyze_file, file_change, self.pipeline_name
                ): file_change
                for file_change in context.file_changes
            }
            for future in future_to_file:
                file_change = future_to_file[future]
                try:
                    file_results = future.result()
                    if file_results:
                        results[file_change.file_path] = file_results
                except Exception as e:
                    logger.error(
                        f"Error analyzing file {file_change.file_path}: {e}"
                    )

        return results


class CrossFileAnalysisStage(AnalysisPipelineStage):
    """A stage that analyzes relationships between files."""

    def __init__(
        self,
        name: str = "Cross-File Analysis",
        description: str = "Analyzes relationships between files",
        pipeline_name: Optional[str] = None,
    ):
        """Initialize the cross-file analysis stage.

        Args:
            name: The name of the stage.
            description: A description of what the stage does.
            pipeline_name: The name of the pipeline to use for analysis.
        """
        super().__init__(name, description)
        self.pipeline_name = pipeline_name

    def process(
        self, context: AnalysisContext, engine: AnalysisEngine
    ) -> Dict[Path, List[AnalysisResult]]:
        """Process the analysis context and return results.

        Args:
            context: The analysis context.
            engine: The analysis engine.

        Returns:
            A dictionary mapping file paths to lists of analysis results.
        """
        # This is a placeholder implementation
        # In a real implementation, we would analyze relationships between files
        # using the graph-sitter codebase representation
        return {}


class ResultAggregationStage(AnalysisPipelineStage):
    """A stage that aggregates and prioritizes results."""

    def __init__(
        self,
        name: str = "Result Aggregation",
        description: str = "Aggregates and prioritizes results",
        min_severity: AnalysisResultSeverity = AnalysisResultSeverity.LOW,
    ):
        """Initialize the result aggregation stage.

        Args:
            name: The name of the stage.
            description: A description of what the stage does.
            min_severity: The minimum severity level to include in the results.
        """
        super().__init__(name, description)
        self.min_severity = min_severity

    def process(
        self, context: AnalysisContext, engine: AnalysisEngine
    ) -> Dict[Path, List[AnalysisResult]]:
        """Process the analysis context and return results.

        Args:
            context: The analysis context.
            engine: The analysis engine.

        Returns:
            A dictionary mapping file paths to lists of analysis results.
        """
        # This stage doesn't generate new results, it just filters and sorts existing ones
        # So we'll return an empty dictionary
        return {}

    def aggregate_results(
        self, results: Dict[Path, List[AnalysisResult]]
    ) -> Dict[Path, List[AnalysisResult]]:
        """Aggregate and prioritize results.

        Args:
            results: A dictionary mapping file paths to lists of analysis results.

        Returns:
            A dictionary mapping file paths to lists of filtered and sorted analysis results.
        """
        aggregated_results: Dict[Path, List[AnalysisResult]] = {}
        for file_path, file_results in results.items():
            # Filter results by severity
            filtered_results = [
                r for r in file_results if r.severity >= self.min_severity
            ]
            if filtered_results:
                # Sort results by severity (highest first)
                sorted_results = sorted(
                    filtered_results, key=lambda r: r.severity, reverse=True
                )
                aggregated_results[file_path] = sorted_results
        return aggregated_results


class AnalysisPipelineExecutor:
    """Executes the analysis pipeline."""

    def __init__(self, engine: AnalysisEngine):
        """Initialize the pipeline executor.

        Args:
            engine: The analysis engine.
        """
        self.engine = engine
        self.stages: List[AnalysisPipelineStage] = []

    def add_stage(self, stage: AnalysisPipelineStage) -> None:
        """Add a stage to the pipeline.

        Args:
            stage: The stage to add.
        """
        self.stages.append(stage)

    def execute(
        self, context: AnalysisContext
    ) -> Dict[Path, List[AnalysisResult]]:
        """Execute the pipeline and return results.

        Args:
            context: The analysis context.

        Returns:
            A dictionary mapping file paths to lists of analysis results.
        """
        all_results: Dict[Path, List[AnalysisResult]] = {}
        
        # Execute each stage
        for stage in self.stages:
            logger.info(f"Executing pipeline stage: {stage.name}")
            try:
                stage_results = stage.process(context, self.engine)
                
                # Merge stage results with all results
                for file_path, file_results in stage_results.items():
                    if file_path in all_results:
                        all_results[file_path].extend(file_results)
                    else:
                        all_results[file_path] = file_results
            except Exception as e:
                logger.error(f"Error executing pipeline stage {stage.name}: {e}")
        
        # If the last stage is a result aggregation stage, use it to aggregate results
        if self.stages and isinstance(self.stages[-1], ResultAggregationStage):
            all_results = self.stages[-1].aggregate_results(all_results)
        
        return all_results

