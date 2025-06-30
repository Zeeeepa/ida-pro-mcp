"""
Base test class for rule tests.

This module provides a base test class for testing analysis rules.
"""
import unittest
from typing import List, Dict, Any, Optional

from ..core import BaseRule, AnalysisResult, AnalysisContext


class MockAnalysisContext(AnalysisContext):
    """
    Mock analysis context for testing.
    
    This class provides a mock implementation of AnalysisContext for testing.
    """
    def __init__(self, pr_data: Dict[str, Any] = None, changed_files: List[str] = None, file_contents: Dict[str, str] = None):
        """
        Initialize the mock analysis context.
        
        Args:
            pr_data: Data about the PR being analyzed
            changed_files: List of files changed in the PR
            file_contents: Dictionary mapping file paths to file contents
        """
        super().__init__(pr_data)
        self._changed_files = changed_files or []
        self._file_contents = file_contents or {}
        self._file_diffs = {}
    
    def get_changed_files(self) -> List[str]:
        """
        Get the list of files changed in the PR.
        
        Returns:
            List of file paths that were changed in the PR
        """
        return self._changed_files
    
    def get_file_content(self, file_path: str) -> str:
        """
        Get the content of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Content of the file as a string
        """
        return self._file_contents.get(file_path, "")
    
    def get_file_diff(self, file_path: str) -> str:
        """
        Get the diff for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Diff of the file as a string
        """
        return self._file_diffs.get(file_path, "")
    
    def set_file_diff(self, file_path: str, diff: str) -> None:
        """
        Set the diff for a file.
        
        Args:
            file_path: Path to the file
            diff: Diff of the file as a string
        """
        self._file_diffs[file_path] = diff


class BaseRuleTest(unittest.TestCase):
    """
    Base test class for rule tests.
    
    This class provides common functionality for testing analysis rules.
    """
    def create_context(self, pr_data: Dict[str, Any] = None, changed_files: List[str] = None, file_contents: Dict[str, str] = None) -> MockAnalysisContext:
        """
        Create a mock analysis context for testing.
        
        Args:
            pr_data: Data about the PR being analyzed
            changed_files: List of files changed in the PR
            file_contents: Dictionary mapping file paths to file contents
            
        Returns:
            Mock analysis context
        """
        return MockAnalysisContext(pr_data, changed_files, file_contents)
    
    def assert_rule_results(self, rule: BaseRule, context: AnalysisContext, expected_count: int) -> List[AnalysisResult]:
        """
        Assert that a rule produces the expected number of results.
        
        Args:
            rule: Rule to test
            context: Analysis context to use
            expected_count: Expected number of results
            
        Returns:
            List of analysis results
        """
        results = rule.run(context)
        self.assertEqual(len(results), expected_count, f"Expected {expected_count} results, got {len(results)}")
        return results
    
    def assert_result_contains(self, results: List[AnalysisResult], message_substring: str) -> AnalysisResult:
        """
        Assert that a list of results contains a result with a message containing a substring.
        
        Args:
            results: List of analysis results
            message_substring: Substring to search for in result messages
            
        Returns:
            The matching result
        """
        for result in results:
            if message_substring in result.message:
                return result
        
        self.fail(f"No result found with message containing '{message_substring}'")
    
    def assert_result_file(self, result: AnalysisResult, file_path: str) -> None:
        """
        Assert that a result is for a specific file.
        
        Args:
            result: Analysis result
            file_path: Expected file path
        """
        self.assertEqual(result.file_path, file_path, f"Expected result for file '{file_path}', got '{result.file_path}'")
    
    def assert_result_line(self, result: AnalysisResult, line_number: int) -> None:
        """
        Assert that a result is for a specific line.
        
        Args:
            result: Analysis result
            line_number: Expected line number
        """
        self.assertEqual(result.line_number, line_number, f"Expected result for line {line_number}, got {result.line_number}")
    
    def assert_result_severity(self, result: AnalysisResult, severity: str) -> None:
        """
        Assert that a result has a specific severity.
        
        Args:
            result: Analysis result
            severity: Expected severity
        """
        self.assertEqual(result.severity, severity, f"Expected result with severity '{severity}', got '{result.severity}'")

