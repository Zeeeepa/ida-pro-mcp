"""
Tests for the analysis engine.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ida_pro_mcp.pr_analysis.analyzers.syntax_analyzer import SyntaxAnalyzer
from ida_pro_mcp.pr_analysis.core.analysis_engine import AnalysisEngine, AnalyzerType
from ida_pro_mcp.pr_analysis.core.models import (
    AnalysisResult,
    AnalysisResultSeverity,
    AnalysisResultType,
    CodeElement,
    CodeElementType,
    FileChange,
    Location,
)


class TestAnalysisEngine(unittest.TestCase):
    """Tests for the analysis engine."""

    def setUp(self):
        """Set up the test."""
        self.engine = AnalysisEngine()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.engine.register_analyzer(self.syntax_analyzer)

    def test_register_analyzer(self):
        """Test registering an analyzer."""
        # Create a mock analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.name = "MockAnalyzer"
        mock_analyzer.analyzer_type = AnalyzerType.CUSTOM

        # Register the analyzer
        self.engine.register_analyzer(mock_analyzer)

        # Check that the analyzer was registered
        self.assertIn("MockAnalyzer", self.engine.analyzers)
        self.assertEqual(self.engine.analyzers["MockAnalyzer"], mock_analyzer)

    def test_create_pipeline(self):
        """Test creating a pipeline."""
        # Create a pipeline
        pipeline = self.engine.create_pipeline("test_pipeline", ["SyntaxAnalyzer"])

        # Check that the pipeline was created
        self.assertIn("test_pipeline", self.engine.pipelines)
        self.assertEqual(self.engine.pipelines["test_pipeline"], pipeline)
        self.assertEqual(len(pipeline.analyzers), 1)
        self.assertEqual(pipeline.analyzers[0], self.syntax_analyzer)

    def test_analyze_file(self):
        """Test analyzing a file."""
        # Create a mock file change
        file_change = MagicMock(spec=FileChange)
        file_change.file_path = Path("test.py")
        file_change.language = "python"
        file_change.is_deleted = False
        file_change.new_content = "def test():\n    return 1"

        # Mock the analyze_file method of the syntax analyzer
        mock_result = MagicMock(spec=AnalysisResult)
        self.syntax_analyzer.analyze_file = MagicMock(return_value=[mock_result])

        # Analyze the file
        results = self.engine.analyze_file(file_change)

        # Check that the analyzer was called
        self.syntax_analyzer.analyze_file.assert_called_once_with(file_change)

        # Check that the results were returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_result)

    def test_analyze_code_element(self):
        """Test analyzing a code element."""
        # Create a mock code element
        code_element = MagicMock(spec=CodeElement)
        code_element.element_type = CodeElementType.FUNCTION
        code_element.language = "python"
        code_element.name = "test"
        code_element.content = "def test():\n    return 1"

        # Mock the analyze_code_element method of the syntax analyzer
        mock_result = MagicMock(spec=AnalysisResult)
        self.syntax_analyzer.analyze_code_element = MagicMock(return_value=[mock_result])

        # Analyze the code element
        results = self.engine.analyze_code_element(code_element)

        # Check that the analyzer was called
        self.syntax_analyzer.analyze_code_element.assert_called_once_with(code_element)

        # Check that the results were returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_result)

    def test_analyze_pr_changes(self):
        """Test analyzing PR changes."""
        # Create mock file changes
        file_change1 = MagicMock(spec=FileChange)
        file_change1.file_path = Path("test1.py")
        file_change1.language = "python"
        file_change1.is_deleted = False
        file_change1.new_content = "def test1():\n    return 1"

        file_change2 = MagicMock(spec=FileChange)
        file_change2.file_path = Path("test2.py")
        file_change2.language = "python"
        file_change2.is_deleted = False
        file_change2.new_content = "def test2():\n    return 2"

        # Mock the analyze_file method of the syntax analyzer
        mock_result1 = MagicMock(spec=AnalysisResult)
        mock_result2 = MagicMock(spec=AnalysisResult)
        self.syntax_analyzer.analyze_file = MagicMock(
            side_effect=[[mock_result1], [mock_result2]]
        )

        # Analyze the PR changes
        results = self.engine.analyze_pr_changes([file_change1, file_change2])

        # Check that the analyzer was called for each file
        self.assertEqual(self.syntax_analyzer.analyze_file.call_count, 2)
        self.syntax_analyzer.analyze_file.assert_any_call(file_change1)
        self.syntax_analyzer.analyze_file.assert_any_call(file_change2)

        # Check that the results were returned
        self.assertEqual(len(results), 2)
        self.assertIn(file_change1.file_path, results)
        self.assertIn(file_change2.file_path, results)
        self.assertEqual(results[file_change1.file_path], [mock_result1])
        self.assertEqual(results[file_change2.file_path], [mock_result2])

    def test_filter_results(self):
        """Test filtering results."""
        # Create mock results
        result1 = MagicMock(spec=AnalysisResult)
        result1.severity = AnalysisResultSeverity.LOW
        result1.result_type = AnalysisResultType.STYLE_ISSUE

        result2 = MagicMock(spec=AnalysisResult)
        result2.severity = AnalysisResultSeverity.MEDIUM
        result2.result_type = AnalysisResultType.SEMANTIC_ERROR

        result3 = MagicMock(spec=AnalysisResult)
        result3.severity = AnalysisResultSeverity.HIGH
        result3.result_type = AnalysisResultType.SYNTAX_ERROR

        # Filter by severity
        results = self.engine.filter_results(
            [result1, result2, result3], severity=AnalysisResultSeverity.MEDIUM
        )
        self.assertEqual(len(results), 2)
        self.assertIn(result2, results)
        self.assertIn(result3, results)

        # Filter by type
        results = self.engine.filter_results(
            [result1, result2, result3], result_type=AnalysisResultType.SEMANTIC_ERROR
        )
        self.assertEqual(len(results), 1)
        self.assertIn(result2, results)

        # Filter by both
        results = self.engine.filter_results(
            [result1, result2, result3],
            severity=AnalysisResultSeverity.MEDIUM,
            result_type=AnalysisResultType.SEMANTIC_ERROR,
        )
        self.assertEqual(len(results), 1)
        self.assertIn(result2, results)

    def test_sort_results(self):
        """Test sorting results."""
        # Create mock results
        result1 = MagicMock(spec=AnalysisResult)
        result1.severity = AnalysisResultSeverity.LOW
        result1.file_path = Path("test.py")
        result1.line = 10
        result1.column = 5

        result2 = MagicMock(spec=AnalysisResult)
        result2.severity = AnalysisResultSeverity.MEDIUM
        result2.file_path = Path("test.py")
        result2.line = 5
        result2.column = 10

        result3 = MagicMock(spec=AnalysisResult)
        result3.severity = AnalysisResultSeverity.HIGH
        result3.file_path = Path("test.py")
        result3.line = 15
        result3.column = 15

        # Sort by severity
        results = self.engine.sort_results([result1, result2, result3], by_severity=True)
        self.assertEqual(results, [result3, result2, result1])

        # Sort by location
        results = self.engine.sort_results([result1, result2, result3], by_severity=False)
        self.assertEqual(results, [result2, result1, result3])


if __name__ == "__main__":
    unittest.main()

