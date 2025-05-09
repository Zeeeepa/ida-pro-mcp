# PR Static Analysis System

A system for static analysis of pull requests.

## Overview

This system provides a framework for analyzing pull requests and identifying potential issues. It is designed to be extensible, allowing users to define custom rules for their specific needs.

## Features

- Analyze pull requests for potential issues
- Extensible rule system
- Configurable analysis pipeline
- Support for plugins and extensions
- Detailed reporting of analysis results

## Architecture

The system is organized into the following components:

- **Core**: Contains the main analysis pipeline and infrastructure
  - `analysis_context.py`: Holds the state during analysis
  - `rule_engine.py`: Manages and executes analysis rules
  - `pr_analyzer.py`: Orchestrates the analysis process
- **Rules**: Contains the rules for PR analysis
  - `base_rule.py`: Base class for all rules
- **Config**: Contains configuration handling
  - `config_model.py`: Configuration models
  - `default_config.py`: Default configuration
- **Utils**: Contains utility functions
  - `helpers.py`: Utility functions for the system

## Usage

```python
from pr_static_analysis import PRAnalyzer, PRData, AnalysisConfig
from datetime import datetime

# Create PR data
pr_data = PRData(
    pr_id="123",
    title="Add new feature",
    description="This PR adds a new feature",
    author="user",
    base_branch="main",
    head_branch="feature",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    files_changed=["file1.py", "file2.py"]
)

# Create analyzer with default config
analyzer = PRAnalyzer(AnalysisConfig())

# Analyze PR
results = analyzer.analyze_pr(pr_data)

# Print results
for result in results:
    print(f"{result.rule_id}: {result.status} - {result.message}")
```

## Creating Custom Rules

To create a custom rule, inherit from the `BaseRule` class and implement the `analyze` method:

```python
from pr_static_analysis import BaseRule, PRAnalysisContext, AnalysisResult
from typing import List

class MyCustomRule(BaseRule):
    RULE_ID = "my_custom_rule"
    CATEGORY = "custom"
    DESCRIPTION = "My custom rule"
    SEVERITY = "warning"
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        # Implement your rule logic here
        results = []
        
        # Example: Check if any Python files were changed
        for file_path in context.pr_data.files_changed:
            if file_path.endswith(".py"):
                results.append(AnalysisResult(
                    rule_id=self.RULE_ID,
                    status="pass",
                    message="Python file changed",
                    file_path=file_path
                ))
                
        return results
```

## Configuration

The system can be configured using a JSON or YAML file:

```yaml
# Example configuration
max_workers: 8
parallel_execution: true
include_categories:
  - security
  - performance
exclude_rules:
  - unused_import
output_format: json
output_file: results.json
```

## License

MIT

