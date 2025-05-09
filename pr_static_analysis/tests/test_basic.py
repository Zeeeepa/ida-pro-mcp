"""
Basic tests for the PR static analysis system.
"""
import unittest
from datetime import datetime

from pr_static_analysis import (
    PRAnalysisContext, PRData, AnalysisResult,
    RuleEngine, PRAnalyzer, BaseRule, AnalysisConfig
)

class SimpleRule(BaseRule):
    """A simple rule for testing."""
    
    RULE_ID = "simple_rule"
    CATEGORY = "test"
    DESCRIPTION = "A simple rule for testing"
    SEVERITY = "info"
    
    def analyze(self, context):
        """Always returns a passing result."""
        return [
            AnalysisResult(
                rule_id=self.RULE_ID,
                status="pass",
                message="Simple rule passed",
                details={"test": True}
            )
        ]

class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the PR static analysis system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pr_data = PRData(
            pr_id="123",
            title="Test PR",
            description="A test PR",
            author="test_user",
            base_branch="main",
            head_branch="feature",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            files_changed=["test.py"]
        )
        
        self.context = PRAnalysisContext(self.pr_data)
        self.rule_engine = RuleEngine()
        self.rule_engine.register_rule(SimpleRule)
        
    def test_rule_registration(self):
        """Test rule registration."""
        self.assertIn("simple_rule", self.rule_engine.get_all_rules())
        
    def test_rule_execution(self):
        """Test rule execution."""
        results = self.rule_engine.execute_rule("simple_rule", self.context)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_id, "simple_rule")
        self.assertEqual(results[0].status, "pass")
        
    def test_analyzer(self):
        """Test the analyzer."""
        config = AnalysisConfig()
        analyzer = PRAnalyzer(config)
        
        # Register the rule manually since we're not loading from a directory
        analyzer.rule_engine.register_rule(SimpleRule)
        
        results = analyzer.analyze_pr(self.pr_data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_id, "simple_rule")
        self.assertEqual(results[0].status, "pass")
        
if __name__ == "__main__":
    unittest.main()

