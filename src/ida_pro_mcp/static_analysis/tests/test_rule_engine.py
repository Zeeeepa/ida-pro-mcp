"""
Tests for the rule engine.

This module contains tests for the rule engine and PR analyzer.
"""
import unittest
from unittest.mock import MagicMock, patch

from .test_base import BaseRuleTest, MockAnalysisContext
from ..core import BaseRule, AnalysisResult, RuleEngine
from ..pr_analyzer import PRAnalyzer


class MockRule(BaseRule):
    """Mock rule for testing."""
    
    def __init__(self, name="mock_rule", description="Mock rule for testing", severity="warning", should_run_result=True, run_results=None):
        """
        Initialize the mock rule.
        
        Args:
            name: Name of the rule
            description: Description of the rule
            severity: Severity of the rule
            should_run_result: Result to return from should_run()
            run_results: Results to return from run()
        """
        super().__init__(name, description, severity)
        self.should_run_result = should_run_result
        self.run_results = run_results or []
        self.should_run_called = False
        self.run_called = False
    
    def should_run(self, context):
        """Mock implementation of should_run()."""
        self.should_run_called = True
        return self.should_run_result
    
    def run(self, context):
        """Mock implementation of run()."""
        self.run_called = True
        return self.run_results


class TestRuleEngine(unittest.TestCase):
    """Tests for the RuleEngine class."""
    
    def test_run_rules(self):
        """Test that run_rules() runs all rules and collects results."""
        # Create mock rules
        rule1 = MockRule(name="rule1", run_results=[
            AnalysisResult(rule_name="rule1", message="Result 1")
        ])
        rule2 = MockRule(name="rule2", run_results=[
            AnalysisResult(rule_name="rule2", message="Result 2"),
            AnalysisResult(rule_name="rule2", message="Result 3")
        ])
        
        # Create rule engine
        engine = RuleEngine([rule1, rule2])
        
        # Create context
        context = MockAnalysisContext()
        
        # Run rules
        results = engine.run_rules(context)
        
        # Check that rules were called
        self.assertTrue(rule1.should_run_called)
        self.assertTrue(rule1.run_called)
        self.assertTrue(rule2.should_run_called)
        self.assertTrue(rule2.run_called)
        
        # Check results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].rule_name, "rule1")
        self.assertEqual(results[0].message, "Result 1")
        self.assertEqual(results[1].rule_name, "rule2")
        self.assertEqual(results[1].message, "Result 2")
        self.assertEqual(results[2].rule_name, "rule2")
        self.assertEqual(results[2].message, "Result 3")
    
    def test_run_rule_by_name(self):
        """Test that run_rule_by_name() runs a specific rule and collects results."""
        # Create mock rules
        rule1 = MockRule(name="rule1", run_results=[
            AnalysisResult(rule_name="rule1", message="Result 1")
        ])
        rule2 = MockRule(name="rule2", run_results=[
            AnalysisResult(rule_name="rule2", message="Result 2"),
            AnalysisResult(rule_name="rule2", message="Result 3")
        ])
        
        # Create rule engine
        engine = RuleEngine([rule1, rule2])
        
        # Create context
        context = MockAnalysisContext()
        
        # Run rule by name
        results = engine.run_rule_by_name("rule2", context)
        
        # Check that only rule2 was called
        self.assertFalse(rule1.should_run_called)
        self.assertFalse(rule1.run_called)
        self.assertTrue(rule2.should_run_called)
        self.assertTrue(rule2.run_called)
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].rule_name, "rule2")
        self.assertEqual(results[0].message, "Result 2")
        self.assertEqual(results[1].rule_name, "rule2")
        self.assertEqual(results[1].message, "Result 3")
    
    def test_rule_should_not_run(self):
        """Test that rules are not run if should_run() returns False."""
        # Create mock rules
        rule1 = MockRule(name="rule1", should_run_result=False, run_results=[
            AnalysisResult(rule_name="rule1", message="Result 1")
        ])
        rule2 = MockRule(name="rule2", run_results=[
            AnalysisResult(rule_name="rule2", message="Result 2")
        ])
        
        # Create rule engine
        engine = RuleEngine([rule1, rule2])
        
        # Create context
        context = MockAnalysisContext()
        
        # Run rules
        results = engine.run_rules(context)
        
        # Check that rule1 was not run
        self.assertTrue(rule1.should_run_called)
        self.assertFalse(rule1.run_called)
        self.assertTrue(rule2.should_run_called)
        self.assertTrue(rule2.run_called)
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_name, "rule2")
        self.assertEqual(results[0].message, "Result 2")


class TestPRAnalyzer(unittest.TestCase):
    """Tests for the PRAnalyzer class."""
    
    def test_analyze_pr(self):
        """Test that analyze_pr() runs all rules and collects results."""
        # Create mock rule engine
        rule_engine = MagicMock()
        rule_engine.run_rules.return_value = [
            AnalysisResult(rule_name="rule1", message="Result 1"),
            AnalysisResult(rule_name="rule2", message="Result 2")
        ]
        
        # Create PR analyzer
        analyzer = PRAnalyzer(rule_engine)
        
        # Analyze PR
        pr_data = {"id": 123, "title": "Test PR"}
        results = analyzer.analyze_pr(pr_data)
        
        # Check that rule engine was called
        rule_engine.run_rules.assert_called_once()
        context = rule_engine.run_rules.call_args[0][0]
        self.assertEqual(context.pr_data, pr_data)
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].rule_name, "rule1")
        self.assertEqual(results[0].message, "Result 1")
        self.assertEqual(results[1].rule_name, "rule2")
        self.assertEqual(results[1].message, "Result 2")
    
    def test_analyze_pr_by_category(self):
        """Test that analyze_pr_by_category() runs rules in a category and collects results."""
        # Create mock rule engine
        rule_engine = MagicMock()
        rule_engine.run_rules_by_category.return_value = [
            AnalysisResult(rule_name="rule1", message="Result 1")
        ]
        
        # Create PR analyzer
        analyzer = PRAnalyzer(rule_engine)
        
        # Analyze PR by category
        pr_data = {"id": 123, "title": "Test PR"}
        results = analyzer.analyze_pr_by_category(pr_data, "code_integrity")
        
        # Check that rule engine was called
        rule_engine.run_rules_by_category.assert_called_once_with("code_integrity", unittest.mock.ANY)
        context = rule_engine.run_rules_by_category.call_args[0][1]
        self.assertEqual(context.pr_data, pr_data)
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_name, "rule1")
        self.assertEqual(results[0].message, "Result 1")
    
    def test_analyze_pr_by_rule(self):
        """Test that analyze_pr_by_rule() runs a specific rule and collects results."""
        # Create mock rule engine
        rule_engine = MagicMock()
        rule_engine.run_rule_by_name.return_value = [
            AnalysisResult(rule_name="rule1", message="Result 1")
        ]
        
        # Create PR analyzer
        analyzer = PRAnalyzer(rule_engine)
        
        # Analyze PR by rule
        pr_data = {"id": 123, "title": "Test PR"}
        results = analyzer.analyze_pr_by_rule(pr_data, "rule1")
        
        # Check that rule engine was called
        rule_engine.run_rule_by_name.assert_called_once_with("rule1", unittest.mock.ANY)
        context = rule_engine.run_rule_by_name.call_args[0][1]
        self.assertEqual(context.pr_data, pr_data)
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_name, "rule1")
        self.assertEqual(results[0].message, "Result 1")


if __name__ == "__main__":
    unittest.main()

