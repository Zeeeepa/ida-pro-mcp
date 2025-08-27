"""
Unit tests for the PR analyzer components.
"""

import unittest
from unittest.mock import MagicMock, patch

from ida_pro_mcp.github_integration.pr_analyzer import (
    PRAnalyzer,
    RuleEngine,
    AnalysisContext,
    CorePRAnalyzer
)


class TestRuleEngine(unittest.TestCase):
    """
    Test cases for the RuleEngine class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.rule_engine = RuleEngine()
    
    def test_init_no_rules(self):
        """
        Test initialization with no rules.
        """
        self.assertEqual(self.rule_engine.rules, [])
    
    def test_init_with_rules(self):
        """
        Test initialization with rules.
        """
        rules = [{"id": "rule1"}, {"id": "rule2"}]
        rule_engine = RuleEngine(rules)
        self.assertEqual(rule_engine.rules, rules)
    
    def test_add_rule(self):
        """
        Test adding a rule.
        """
        rule = {"id": "rule1"}
        self.rule_engine.add_rule(rule)
        self.assertEqual(self.rule_engine.rules, [rule])
    
    def test_apply_rules(self):
        """
        Test applying rules to a file.
        """
        # This is a placeholder test since the actual implementation
        # of _apply_rule is a placeholder
        file_path = "test.py"
        content = "def test(): pass"
        
        issues = self.rule_engine.apply_rules(file_path, content)
        self.assertEqual(issues, [])


class TestAnalysisContext(unittest.TestCase):
    """
    Test cases for the AnalysisContext class.
    """
    
    def test_init(self):
        """
        Test initialization.
        """
        repo = "test/repo"
        pr_number = 123
        pr_data = {
            "number": 123,
            "changed_files": ["file1", "file2"],
            "commits": ["commit1", "commit2"],
            "base_commit": "base_sha",
            "head_commit": "head_sha"
        }
        
        context = AnalysisContext(repo, pr_number, pr_data)
        
        self.assertEqual(context.repo, repo)
        self.assertEqual(context.pr_number, pr_number)
        self.assertEqual(context.pr_data, pr_data)
        self.assertEqual(context.files, ["file1", "file2"])
        self.assertEqual(context.commits, ["commit1", "commit2"])
        self.assertEqual(context.base_commit, "base_sha")
        self.assertEqual(context.head_commit, "head_sha")


class TestCorePRAnalyzer(unittest.TestCase):
    """
    Test cases for the CorePRAnalyzer class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.pr_client = MagicMock()
        self.rule_engine = MagicMock()
        self.analyzer = CorePRAnalyzer(self.pr_client, self.rule_engine)
    
    def test_init(self):
        """
        Test initialization.
        """
        self.assertEqual(self.analyzer.pr_client, self.pr_client)
        self.assertEqual(self.analyzer.rule_engine, self.rule_engine)
    
    def test_init_default_rule_engine(self):
        """
        Test initialization with default rule engine.
        """
        analyzer = CorePRAnalyzer(self.pr_client)
        self.assertEqual(analyzer.pr_client, self.pr_client)
        self.assertIsInstance(analyzer.rule_engine, RuleEngine)
    
    def test_analyze_pr(self):
        """
        Test analyzing a PR.
        """
        # Mock PR data
        repo = "test/repo"
        pr_number = 123
        pr_data = {
            "number": 123,
            "changed_files": [
                MagicMock(filename="file1.py", status="modified", patch="patch1"),
                MagicMock(filename="file2.py", status="modified", patch="patch2"),
                MagicMock(filename="file3.py", status="removed", patch=None)
            ]
        }
        
        # Mock file content
        self.pr_client.get_pr.return_value = pr_data
        self.pr_client.get_file_content.side_effect = ["content1", "content2", None]
        
        # Mock rule engine
        self.rule_engine.apply_rules.side_effect = [
            [{"severity": "error", "message": "Error in file1"}],
            [{"severity": "warning", "message": "Warning in file2"}]
        ]
        
        # Call the method
        result = self.analyzer.analyze_pr(repo, pr_number)
        
        # Verify the result
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0]["severity"], "error")
        self.assertEqual(result["issues"][1]["severity"], "warning")
        self.assertEqual(result["summary"]["total_files"], 3)
        self.assertEqual(result["summary"]["analyzed_files"], 2)
        
        # Verify method calls
        self.pr_client.get_pr.assert_called_once_with(repo, pr_number)
        self.pr_client.get_file_content.assert_any_call(repo, pr_number, "file1.py")
        self.pr_client.get_file_content.assert_any_call(repo, pr_number, "file2.py")
        self.rule_engine.apply_rules.assert_any_call("file1.py", "content1")
        self.rule_engine.apply_rules.assert_any_call("file2.py", "content2")
    
    def test_analyze_pr_with_provided_data(self):
        """
        Test analyzing a PR with provided data.
        """
        # Mock PR data
        repo = "test/repo"
        pr_number = 123
        pr_data = {
            "number": 123,
            "changed_files": [
                MagicMock(filename="file1.py", status="modified", patch="patch1")
            ]
        }
        
        # Mock file content
        self.pr_client.get_file_content.return_value = "content1"
        
        # Mock rule engine
        self.rule_engine.apply_rules.return_value = [
            {"severity": "error", "message": "Error in file1"}
        ]
        
        # Call the method with provided data
        result = self.analyzer.analyze_pr(repo, pr_number, pr_data)
        
        # Verify the result
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["severity"], "error")
        self.assertEqual(result["summary"]["total_files"], 1)
        self.assertEqual(result["summary"]["analyzed_files"], 1)
        
        # Verify method calls
        self.pr_client.get_pr.assert_not_called()
        self.pr_client.get_file_content.assert_called_once_with(repo, pr_number, "file1.py")
        self.rule_engine.apply_rules.assert_called_once_with("file1.py", "content1")
    
    def test_should_analyze_file(self):
        """
        Test determining if a file should be analyzed.
        """
        # File that should be analyzed
        file1 = MagicMock(status="modified", patch="patch1")
        self.assertTrue(self.analyzer._should_analyze_file(file1))
        
        # File that should not be analyzed (removed)
        file2 = MagicMock(status="removed", patch="patch2")
        self.assertFalse(self.analyzer._should_analyze_file(file2))
        
        # File that should not be analyzed (binary)
        file3 = MagicMock(status="modified", patch=None)
        self.assertFalse(self.analyzer._should_analyze_file(file3))
    
    def test_generate_recommendations(self):
        """
        Test generating recommendations based on issues.
        """
        # Issues with errors
        issues1 = [
            {"severity": "error", "message": "Error 1"},
            {"severity": "warning", "message": "Warning 1"}
        ]
        
        recommendations1 = self.analyzer._generate_recommendations(issues1)
        self.assertIn("Fix all errors before merging the PR", recommendations1)
        
        # Issues without errors
        issues2 = [
            {"severity": "warning", "message": "Warning 1"},
            {"severity": "info", "message": "Info 1"}
        ]
        
        recommendations2 = self.analyzer._generate_recommendations(issues2)
        self.assertEqual(recommendations2, [])


if __name__ == "__main__":
    unittest.main()

