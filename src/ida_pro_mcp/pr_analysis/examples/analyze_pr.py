"""
Example script for analyzing a PR using the PR static analysis system.
"""

import argparse
import logging
import sys
from pathlib import Path

from ida_pro_mcp.pr_analysis.analyzers.semantic_analyzer import SemanticAnalyzer
from ida_pro_mcp.pr_analysis.analyzers.style_analyzer import StyleAnalyzer
from ida_pro_mcp.pr_analysis.analyzers.syntax_analyzer import SyntaxAnalyzer
from ida_pro_mcp.pr_analysis.core.analysis_engine import AnalysisEngine
from ida_pro_mcp.pr_analysis.core.graph_sitter_adapter import GraphSitterAdapter
from ida_pro_mcp.pr_analysis.core.models import AnalysisResultSeverity
from ida_pro_mcp.pr_analysis.core.pipeline import (
    AnalysisPipelineExecutor,
    CrossFileAnalysisStage,
    FileAnalysisStage,
    ResultAggregationStage,
)
from ida_pro_mcp.pr_analysis.core.pr_changes import PRChangesExtractor


def setup_logging():
    """Set up logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze a PR for issues")
    parser.add_argument(
        "--repo-path", type=str, required=True, help="Path to the repository"
    )
    parser.add_argument(
        "--base-commit", type=str, required=True, help="Base commit hash"
    )
    parser.add_argument(
        "--head-commit", type=str, required=True, help="Head commit hash"
    )
    parser.add_argument(
        "--file-paths",
        type=str,
        nargs="*",
        help="Optional list of file paths to analyze",
    )
    parser.add_argument(
        "--min-severity",
        type=str,
        choices=["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
        default="LOW",
        help="Minimum severity level to report",
    )
    return parser.parse_args()


def main():
    """Main function."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    args = parse_args()
    repository_path = Path(args.repo_path)
    base_commit = args.base_commit
    head_commit = args.head_commit
    file_paths = [Path(p) for p in args.file_paths] if args.file_paths else None
    min_severity = getattr(AnalysisResultSeverity, args.min_severity)

    try:
        # Create a graph-sitter adapter
        # In a real implementation, we would initialize this with a real CodebaseContext
        graph_sitter_adapter = GraphSitterAdapter(None)

        # Create a PR changes extractor
        pr_changes_extractor = PRChangesExtractor(graph_sitter_adapter)

        # Extract changes from the PR
        logger.info("Extracting changes from PR...")
        context = pr_changes_extractor.extract_changes(
            repository_path, base_commit, head_commit, file_paths
        )
        logger.info(f"Extracted {len(context.file_changes)} file changes")

        # Create an analysis engine
        logger.info("Creating analysis engine...")
        engine = AnalysisEngine()

        # Register analyzers
        engine.register_analyzer(SyntaxAnalyzer())
        engine.register_analyzer(StyleAnalyzer())
        engine.register_analyzer(SemanticAnalyzer())

        # Create a pipeline executor
        logger.info("Creating pipeline executor...")
        executor = AnalysisPipelineExecutor(engine)

        # Add pipeline stages
        executor.add_stage(FileAnalysisStage(parallel=True))
        executor.add_stage(CrossFileAnalysisStage())
        executor.add_stage(ResultAggregationStage(min_severity=min_severity))

        # Execute the pipeline
        logger.info("Executing analysis pipeline...")
        results = executor.execute(context)

        # Print results
        logger.info("Analysis results:")
        for file_path, file_results in results.items():
            print(f"\n{file_path}:")
            for result in file_results:
                print(
                    f"  {result.severity.name}: {result.message} (line {result.line}, col {result.column})"
                )
                if result.code:
                    print(f"    Code: {result.code}")
                if result.fix_suggestions:
                    print(f"    Fix suggestions: {', '.join(result.fix_suggestions)}")

        # Return success
        return 0

    except Exception as e:
        logger.error(f"Error analyzing PR: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

