"""
Tests for parameter validation rules.

This module contains tests for the parameter validation rules.
"""
import unittest

from .test_base import BaseRuleTest
from ..rules.parameter_validation_rules import IncorrectParameterTypeRule, MissingParameterRule, InconsistentParameterRule


class TestIncorrectParameterTypeRule(BaseRuleTest):
    """Tests for the IncorrectParameterTypeRule."""
    
    def test_correct_parameter_types(self):
        """Test that no results are produced when parameter types are used correctly."""
        rule = IncorrectParameterTypeRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1: int, param2: str):
    return param1 + int(param2)
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_incorrect_parameter_type(self):
        """Test that a result is produced when a parameter type is used incorrectly."""
        rule = IncorrectParameterTypeRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1: int, param2: str):
    return param1 + param2.lower()
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("param1", result.message)
        self.assertIn("int", result.message)
        self.assertEqual(result.file_path, "test.py")
    
    def test_syntax_error(self):
        """Test that a result is produced when the file has syntax errors."""
        rule = IncorrectParameterTypeRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1: int, param2: str):
    return param1 + param2.lower()
    }
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("syntax errors", result.message)
        self.assertEqual(result.file_path, "test.py")


class TestMissingParameterRule(BaseRuleTest):
    """Tests for the MissingParameterRule."""
    
    def test_all_parameters_provided(self):
        """Test that no results are produced when all parameters are provided."""
        rule = MissingParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    return param1 + param2

result = test_function(1, 2)
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_missing_parameter(self):
        """Test that a result is produced when a parameter is missing."""
        rule = MissingParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    return param1 + param2

result = test_function(1)
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("missing required parameters", result.message)
        self.assertIn("param2", result.message)
        self.assertEqual(result.file_path, "test.py")
    
    def test_default_parameter(self):
        """Test that no results are produced when a parameter with a default value is not provided."""
        rule = MissingParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2=2):
    return param1 + param2

result = test_function(1)
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)


class TestInconsistentParameterRule(BaseRuleTest):
    """Tests for the InconsistentParameterRule."""
    
    def test_consistent_parameters(self):
        """Test that no results are produced when parameters are consistent."""
        rule = InconsistentParameterRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
def test_function(param1, param2):
    return param1 + param2

def other_function(other_param):
    return other_param
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_inconsistent_parameter_count(self):
        """Test that a result is produced when parameter counts are inconsistent."""
        rule = InconsistentParameterRule()
        context = self.create_context(
            changed_files=["test1.py", "test2.py"],
            file_contents={
                "test1.py": """
def test_function(param1, param2):
    return param1 + param2
""",
                "test2.py": """
def test_function(param1):
    return param1
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("inconsistent number of parameters", result.message)
        self.assertIn("test_function", result.message)
    
    def test_inconsistent_parameter_names(self):
        """Test that a result is produced when parameter names are inconsistent."""
        rule = InconsistentParameterRule()
        context = self.create_context(
            changed_files=["test1.py", "test2.py"],
            file_contents={
                "test1.py": """
def test_function(param1, param2):
    return param1 + param2
""",
                "test2.py": """
def test_function(param1, different_param):
    return param1 + different_param
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("inconsistent parameter name", result.message)
        self.assertIn("test_function", result.message)
        self.assertIn("param2", result.message)
        self.assertIn("different_param", result.message)


if __name__ == "__main__":
    unittest.main()

