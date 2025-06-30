"""
Tests for code integrity rules.

This module contains tests for the code integrity rules.
"""
import unittest

from .test_base import BaseRuleTest
from ..rules.code_integrity_rules import UnusedParameterRule, ComplexityRule, DuplicateCodeRule


class TestUnusedParameterRule(BaseRuleTest):
    """Tests for the UnusedParameterRule."""
    
    def test_no_unused_parameters(self):
        """Test that no results are produced when all parameters are used."""
        rule = UnusedParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    return param1 + param2
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_unused_parameter(self):
        """Test that a result is produced when a parameter is unused."""
        rule = UnusedParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    return param1
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("param2", result.message)
        self.assertIn("test_function", result.message)
        self.assertEqual(result.file_path, "test.py")
    
    def test_skip_self_parameter(self):
        """Test that self parameter is skipped."""
        rule = UnusedParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
class TestClass:
    def test_method(self, param1):
        return 42
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("param1", result.message)
        self.assertIn("test_method", result.message)
        self.assertEqual(result.file_path, "test.py")


class TestComplexityRule(BaseRuleTest):
    """Tests for the ComplexityRule."""
    
    def test_low_complexity(self):
        """Test that no results are produced for low complexity functions."""
        rule = ComplexityRule(max_complexity=5)
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    return param1 + param2
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_high_complexity(self):
        """Test that a result is produced for high complexity functions."""
        rule = ComplexityRule(max_complexity=5)
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    if param1 > 0:
        if param2 > 0:
            return 1
        elif param2 < 0:
            return 2
        else:
            return 3
    elif param1 < 0:
        if param2 > 0:
            return 4
        elif param2 < 0:
            return 5
        else:
            return 6
    else:
        return 7
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("test_function", result.message)
        self.assertIn("complexity", result.message)
        self.assertEqual(result.file_path, "test.py")
        self.assertGreater(result.additional_info["complexity"], 5)


class TestDuplicateCodeRule(BaseRuleTest):
    """Tests for the DuplicateCodeRule."""
    
    def test_no_duplicates(self):
        """Test that no results are produced when there are no duplicates."""
        rule = DuplicateCodeRule(min_lines=3)
        context = self.create_context(
            changed_files=["test1.py", "test2.py"],
            file_contents={
                "test1.py": """
def test_function1():
    return 1

def test_function2():
    return 2
""",
                "test2.py": """
def test_function3():
    return 3

def test_function4():
    return 4
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_duplicate_code(self):
        """Test that a result is produced when there are duplicates."""
        rule = DuplicateCodeRule(min_lines=3)
        context = self.create_context(
            changed_files=["test1.py", "test2.py"],
            file_contents={
                "test1.py": """
def test_function1():
    a = 1
    b = 2
    c = 3
    return a + b + c

def test_function2():
    return 2
""",
                "test2.py": """
def test_function3():
    a = 1
    b = 2
    c = 3
    return a + b + c

def test_function4():
    return 4
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("Duplicate code block", result.message)
        self.assertEqual(result.file_path, "test1.py")
        self.assertEqual(result.additional_info["duplicate_file"], "test2.py")


if __name__ == "__main__":
    unittest.main()

