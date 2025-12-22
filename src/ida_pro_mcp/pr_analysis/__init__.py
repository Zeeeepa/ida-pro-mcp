"""
PR static analysis system.

This package implements a PR static analysis system that analyzes code changes
in pull requests and identifies potential issues.
"""

from ida_pro_mcp.pr_analysis.core.analysis_engine import AnalysisEngine
from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisContext,
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    CodeElement,
    CodeElementType,
    FileChange,
    Location,
)
from ida_pro_mcp.pr_analysis.core.pipeline import (
    AnalysisPipelineExecutor,
    AnalysisPipelineStage,
    FileAnalysisStage,
    CrossFileAnalysisStage,
    ResultAggregationStage,
)
from ida_pro_mcp.pr_analysis.core.pr_changes import PRChangesExtractor

