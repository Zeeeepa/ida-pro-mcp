# PR Static Analysis System

This package implements a PR static analysis system that analyzes code changes in pull requests and identifies potential issues.

## Overview

The PR static analysis system is designed to analyze code changes in pull requests and identify potential issues such as syntax errors, style violations, and logical problems. It integrates with the codebase representation from graph-sitter and supports different types of analysis.

## Components

### Core Analysis Engine

The core analysis engine (`AnalysisEngine`) coordinates different analyzers and provides methods for analyzing files, functions, classes, and other code elements. It supports different programming languages and can be extended with custom analyzers.

### Analysis Pipeline

The analysis pipeline processes PR changes in stages, including:

1. File Analysis: Analyzes individual files for issues
2. Cross-File Analysis: Analyzes relationships between files
3. Result Aggregation: Aggregates and prioritizes results

The pipeline supports parallel analysis of independent files for improved performance.

### Graph-Sitter Integration

The system integrates with graph-sitter's codebase representation through adapter classes that work with graph-sitter's `CodebaseContext`. It provides utilities for traversing the code graph and accessing code elements and their relationships.

### Analyzers

The system includes several built-in analyzers:

- **Syntax Analyzer**: Detects syntax errors using the parser from graph-sitter
- **Style Analyzer**: Checks code for formatting and convention issues
- **Semantic Analyzer**: Detects logical issues in code

### Models

The system defines models for representing analysis findings, including:

- **AnalysisResult**: Represents a finding from an analyzer
- **CodeElement**: Represents a code element (file, class, function, etc.)
- **FileChange**: Represents a change to a file in a PR
- **Location**: Represents a location in a file

## Usage

Here's a simple example of how to use the PR static analysis system:

```python
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

# Create a graph-sitter adapter
graph_sitter_adapter = GraphSitterAdapter(codebase_context)

# Create a PR changes extractor
pr_changes_extractor = PRChangesExtractor(graph_sitter_adapter)

# Extract changes from the PR
context = pr_changes_extractor.extract_changes(
    repository_path, base_commit, head_commit, file_paths
)

# Create an analysis engine
engine = AnalysisEngine()

# Register analyzers
engine.register_analyzer(SyntaxAnalyzer())
engine.register_analyzer(StyleAnalyzer())
engine.register_analyzer(SemanticAnalyzer())

# Create a pipeline executor
executor = AnalysisPipelineExecutor(engine)

# Add pipeline stages
executor.add_stage(FileAnalysisStage(parallel=True))
executor.add_stage(CrossFileAnalysisStage())
executor.add_stage(ResultAggregationStage(min_severity=AnalysisResultSeverity.LOW))

# Execute the pipeline
results = executor.execute(context)

# Process results
for file_path, file_results in results.items():
    print(f"\n{file_path}:")
    for result in file_results:
        print(f"  {result.severity.name}: {result.message} (line {result.line}, col {result.column})")
```

## Extending the System

### Adding a Custom Analyzer

You can create a custom analyzer by subclassing the `Analyzer` class:

```python
from ida_pro_mcp.pr_analysis.core.analysis_engine import Analyzer, AnalyzerType
from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    CodeElement,
    FileChange,
    Location,
)

class CustomAnalyzer(Analyzer):
    """A custom analyzer."""

    def __init__(self, supported_languages=None):
        """Initialize the custom analyzer."""
        super().__init__(
            name="CustomAnalyzer",
            description="A custom analyzer",
            analyzer_type=AnalyzerType.CUSTOM,
            supported_languages=supported_languages,
        )

    def analyze_file(self, file_change: FileChange) -> List[AnalysisResult]:
        """Analyze a file."""
        # Implement your analysis logic here
        results = []
        # ...
        return results

    def analyze_code_element(self, element: CodeElement) -> List[AnalysisResult]:
        """Analyze a code element."""
        # Implement your analysis logic here
        results = []
        # ...
        return results
```

### Adding a Custom Pipeline Stage

You can create a custom pipeline stage by subclassing the `AnalysisPipelineStage` class:

```python
from ida_pro_mcp.pr_analysis.core.analysis_engine import AnalysisEngine
from ida_pro_mcp.pr_analysis.core.models import AnalysisContext, AnalysisResult
from ida_pro_mcp.pr_analysis.core.pipeline import AnalysisPipelineStage

class CustomStage(AnalysisPipelineStage):
    """A custom pipeline stage."""

    def __init__(self, name="Custom Stage", description="A custom pipeline stage"):
        """Initialize the custom stage."""
        super().__init__(name, description)

    def process(self, context: AnalysisContext, engine: AnalysisEngine) -> Dict[Path, List[AnalysisResult]]:
        """Process the analysis context."""
        # Implement your processing logic here
        results = {}
        # ...
        return results
```

