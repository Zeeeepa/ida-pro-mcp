# PR Static Analysis System

A system for analyzing pull requests and providing automated feedback.

## Overview

The PR Static Analysis System is a tool for analyzing pull requests and providing automated feedback. It can be used to:

- Check for code quality issues
- Enforce coding standards
- Detect potential bugs
- Provide suggestions for improvements

The system is designed to be extensible, allowing for easy addition of new rules and features.

## Architecture

The system is organized into the following components:

- **Core**: The core components of the system, including the PR analyzer, rule engine, and analysis context.
- **Rules**: The rules used to analyze pull requests, organized by category.
- **GitHub**: Components for interacting with GitHub's API and webhooks.
- **Reporting**: Components for generating and formatting analysis reports.
- **Utils**: Utility functions used throughout the system.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pr-analysis.git
cd pr-analysis

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from pr_analysis.core.pr_analyzer import PRAnalyzer
from pr_analysis.github.pr_client import PRClient

# Create a PR client
client = PRClient()

# Get PR data
pr_data = client.get_pr("owner", "repo", 123)
files = client.get_pr_files("owner", "repo", 123)

# Convert files to the format expected by the analyzer
file_changes = []
for file in files:
    file_changes.append({
        "filename": file.get("filename"),
        "status": file.get("status"),
        "patch": file.get("patch"),
    })

# Create analyzer
analyzer = PRAnalyzer()

# Analyze PR
context, report = analyzer.analyze_pr(
    pr_id="123",
    repo_name="owner/repo",
    base_branch=pr_data.get("base", {}).get("ref", "main"),
    head_branch=pr_data.get("head", {}).get("ref", "head"),
    file_changes=file_changes,
    output_format="json",
)

# Print report
print(report)
```

### Command Line Usage

```bash
python -m pr_analysis.example 123 owner/repo --format json --output report.json
```

### GitHub Webhook Integration

The system can be integrated with GitHub webhooks to automatically analyze pull requests when they are created or updated.

```python
from pr_analysis.github.webhook_handler import WebhookHandler

# Create webhook handler
handler = WebhookHandler()

# Handle webhook event
result = handler.handle_webhook("pull_request", payload)
```

## Creating Custom Rules

You can create custom rules by inheriting from the `BaseRule` class and implementing the `analyze` method.

```python
from pr_analysis.rules.base_rule import BaseRule
from pr_analysis.core.analysis_context import PRAnalysisContext, AnalysisResult
from typing import List, ClassVar

class MyCustomRule(BaseRule):
    """A custom rule for checking something."""
    
    RULE_ID: ClassVar[str] = "custom.my_rule"
    RULE_NAME: ClassVar[str] = "My Custom Rule"
    RULE_DESCRIPTION: ClassVar[str] = "Checks for something"
    RULE_CATEGORY: ClassVar[str] = "custom"
    
    def analyze(self, context: PRAnalysisContext) -> List[AnalysisResult]:
        """
        Analyze a PR for something.
        
        Args:
            context: The analysis context
            
        Returns:
            A list of analysis results
        """
        results = []
        
        # Analyze the PR
        
        return results
```

## Configuration

The system can be configured using a JSON or YAML file. The configuration file can be specified when creating the analyzer.

```python
from pr_analysis.core.pr_analyzer import PRAnalyzer

# Create analyzer with configuration
analyzer = PRAnalyzer(config_path="config.json")
```

Example configuration file:

```json
{
  "enabled_rules": ["code_integrity.line_length", "parameter.missing_type_hints"],
  "disabled_rules": ["implementation.complexity"],
  "custom_rule_paths": ["path/to/custom/rules"],
  "output_format": "json",
  "output_directory": "reports",
  "github_token": "your-github-token",
  "github_api_url": "https://api.github.com",
  "max_files_per_analysis": 100,
  "max_lines_per_file": 10000,
  "ignore_generated_files": true,
  "ignore_binary_files": true,
  "ignore_deleted_files": false,
  "rule_settings": {
    "code_integrity": {
      "max_file_size": 1000000,
      "max_line_length": 120
    },
    "parameter": {
      "check_types": true,
      "check_defaults": true
    },
    "implementation": {
      "check_complexity": true,
      "max_complexity": 15
    }
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

