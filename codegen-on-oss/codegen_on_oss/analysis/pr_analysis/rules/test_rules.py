"""
Test script for PR static analysis rules.

This script demonstrates how to use the rules to analyze Python code.
"""

import ast
from typing import Any, Dict, List, Optional

from codegen_on_oss.analysis.pr_analysis.rules import (
    BaseRule,
    RuleCategory,
    RuleResult,
    RuleSeverity,
    get_all_rules,
    get_rules_by_category,
    get_rule_by_id,
)


class MockAnalysisContext:
    """Mock analysis context for testing rules."""

    def __init__(self, files: Dict[str, str]):
        """
        Initialize the mock context.

        Args:
            files: Dictionary mapping file paths to file content.
        """
        self.files = files
        self.head_ref = "HEAD"
        self.base_ref = "BASE"

    def get_changed_files(self) -> List[str]:
        """
        Get all changed files.

        Returns:
            A list of file paths.
        """
        return list(self.files.keys())

    def get_file_content(self, file_path: str, ref: str) -> str:
        """
        Get the content of a file at a specific ref.

        Args:
            file_path: Path to the file.
            ref: The ref to get the content from.

        Returns:
            The file content.
        """
        return self.files.get(file_path, "")

    def get_diff(self, file_path: str) -> str:
        """
        Get the diff for a file.

        Args:
            file_path: Path to the file.

        Returns:
            The diff content.
        """
        return ""


def main():
    """Run the test script."""
    # Create a mock context with some Python files
    context = MockAnalysisContext({
        "example.py": """
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    # No docstring
    return a - b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b

def divide(a, b):
    \"\"\"Divide two numbers.\"\"\"
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        \"\"\"Add two numbers.\"\"\"
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        # No docstring
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
""",
        "bad_example.py": """
def add(a, b):
    return a + b

def subtract(a, b)
    return a - b

def multiply(a, b):
    return a * c  # Undefined variable

def process_data(data=[]):  # Mutable default argument
    data.append(1)
    return data

class calculator:  # Class name should be CapWords
    def __init__(self):
        self.History = []  # Variable name should be lowercase_with_underscores
    
    def Add(self, a, b):  # Method name should be lowercase_with_underscores
        result = a + b
        self.History.append(f"{a} + {b} = {result}")
        return result
""",
    })

    # Get all rules
    rules = get_all_rules()

    # Apply each rule to the context
    for rule in rules:
        print(f"Applying rule: {rule.name}")
        results = rule.apply(context)
        
        # Print the results
        if results:
            print(f"Found {len(results)} issues:")
            for result in results:
                print(f"  {result}")
        else:
            print("  No issues found")
        
        print()

    # You can also get rules by category
    code_integrity_rules = get_rules_by_category(RuleCategory.CODE_INTEGRITY)
    print(f"Code integrity rules: {[rule.name for rule in code_integrity_rules]}")

    # Or get a specific rule by ID
    syntax_error_rule = get_rule_by_id("syntax_error")
    if syntax_error_rule:
        print(f"Got rule by ID: {syntax_error_rule.name}")


if __name__ == "__main__":
    main()

