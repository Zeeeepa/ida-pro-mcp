# PR Static Analysis System

This package contains a static analysis system for analyzing pull requests and identifying potential issues in the code.

## Overview

The static analysis system consists of the following components:

- **BaseRule**: Base class for all analysis rules
- **AnalysisResult**: Class representing the result of a rule analysis
- **AnalysisContext**: Class providing context for rule execution
- **RuleEngine**: Class for running rules and collecting results
- **PRAnalyzer**: Class for analyzing pull requests using the rule engine

## Rule Categories

The system includes rules in the following categories:

### Code Integrity Rules

Rules for detecting code quality issues:

- **UnusedParameterRule**: Detects unused parameters in functions
- **ComplexityRule**: Detects functions with high cyclomatic complexity
- **DuplicateCodeRule**: Detects duplicate code blocks

### Parameter Validation Rules

Rules for detecting parameter problems:

- **IncorrectParameterTypeRule**: Detects incorrect parameter types
- **MissingParameterRule**: Detects missing required parameters
- **InconsistentParameterRule**: Detects inconsistent parameter usage

### Implementation Validation Rules

Rules for detecting implementation issues:

- **MissingImplementationRule**: Detects missing implementations
- **IncorrectImplementationRule**: Detects incorrect implementations
- **InconsistentImplementationRule**: Detects inconsistent implementations

## Usage

To analyze a pull request:

```python
from ida_pro_mcp.static_analysis import PRAnalyzer

# Create PR analyzer
analyzer = PRAnalyzer()

# Analyze PR
pr_data = {
    "id": 123,
    "title": "Test PR",
    "changed_files": ["file1.py", "file2.py"],
    # ... other PR data
}
results = analyzer.analyze_pr(pr_data)

# Process results
for result in results:
    print(result)
```

To run specific rule categories:

```python
# Run only code integrity rules
results = analyzer.analyze_pr_by_category(pr_data, "code_integrity")

# Run only parameter validation rules
results = analyzer.analyze_pr_by_category(pr_data, "parameter_validation")

# Run only implementation validation rules
results = analyzer.analyze_pr_by_category(pr_data, "implementation_validation")
```

To run a specific rule:

```python
# Run only the unused parameter rule
results = analyzer.analyze_pr_by_rule(pr_data, "unused_parameter")
```

## Creating Custom Rules

To create a custom rule:

1. Create a new class that inherits from `BaseRule`
2. Implement the `run` method to analyze the code and return results
3. Optionally override the `should_run` method to determine if the rule should run

Example:

```python
from ida_pro_mcp.static_analysis import BaseRule, AnalysisResult, register_rule

@register_rule
class MyCustomRule(BaseRule):
    def __init__(self):
        super().__init__(
            name="my_custom_rule",
            description="My custom rule for detecting issues",
            severity="warning"
        )
    
    def should_run(self, context):
        # Only run on Python files
        return any(file.endswith('.py') for file in context.get_changed_files())
    
    def run(self, context):
        results = []
        
        for file_path in context.get_changed_files():
            if not file_path.endswith('.py'):
                continue
            
            content = context.get_file_content(file_path)
            
            # Analyze the file and add results
            if "TODO" in content:
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains TODO comments",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        return results
```

