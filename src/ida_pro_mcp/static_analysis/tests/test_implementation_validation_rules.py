"""
Tests for implementation validation rules.

This module contains tests for the implementation validation rules.
"""
import unittest

from .test_base import BaseRuleTest
from ..rules.implementation_validation_rules import MissingImplementationRule, IncorrectImplementationRule, InconsistentImplementationRule


class TestMissingImplementationRule(BaseRuleTest):
    """Tests for the MissingImplementationRule."""
    
    def test_all_methods_implemented(self):
        """Test that no results are produced when all abstract methods are implemented."""
        rule = MissingImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def abstract_method(self):
        pass

class ConcreteClass(BaseClass):
    def abstract_method(self):
        return 42
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_missing_implementation(self):
        """Test that a result is produced when an abstract method is not implemented."""
        rule = MissingImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def abstract_method(self):
        pass

class ConcreteClass(BaseClass):
    pass
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("not implemented", result.message)
        self.assertIn("abstract_method", result.message)
        self.assertIn("BaseClass", result.message)
        self.assertEqual(result.file_path, "test.py")


class TestIncorrectImplementationRule(BaseRuleTest):
    """Tests for the IncorrectImplementationRule."""
    
    def test_correct_implementation(self):
        """Test that no results are produced when implementations are correct."""
        rule = IncorrectImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
class BaseClass:
    def method(self, param1, param2):
        pass

class DerivedClass(BaseClass):
    def method(self, param1, param2):
        return param1 + param2
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_incorrect_parameter_count(self):
        """Test that a result is produced when parameter counts are incorrect."""
        rule = IncorrectImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
class BaseClass:
    def method(self, param1, param2):
        pass

class DerivedClass(BaseClass):
    def method(self, param1):
        return param1
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("different number of parameters", result.message)
        self.assertIn("method", result.message)
        self.assertIn("DerivedClass", result.message)
        self.assertIn("BaseClass", result.message)
        self.assertEqual(result.file_path, "test.py")
    
    def test_incorrect_parameter_names(self):
        """Test that a result is produced when parameter names are incorrect."""
        rule = IncorrectImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
class BaseClass:
    def method(self, param1, param2):
        pass

class DerivedClass(BaseClass):
    def method(self, param1, different_param):
        return param1 + different_param
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("different parameter name", result.message)
        self.assertIn("method", result.message)
        self.assertIn("DerivedClass", result.message)
        self.assertIn("BaseClass", result.message)
        self.assertEqual(result.file_path, "test.py")


class TestInconsistentImplementationRule(BaseRuleTest):
    """Tests for the InconsistentImplementationRule."""
    
    def test_consistent_implementations(self):
        """Test that no results are produced when implementations are consistent."""
        rule = InconsistentImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def abstract_method(self):
        pass

class ConcreteClass1(BaseClass):
    def abstract_method(self):
        return 42

class ConcreteClass2(BaseClass):
    def abstract_method(self):
        return 43
"""
            }
        )
        
        self.assert_rule_results(rule, context, 0)
    
    def test_inconsistent_implementations(self):
        """Test that a result is produced when implementations are inconsistent."""
        rule = InconsistentImplementationRule()
        context = self.create_context(
            changed_files=["test.py"],
            file_contents={
                "test.py": """
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def abstract_method(self):
        pass

class ConcreteClass1(BaseClass):
    def abstract_method(self):
        return 42

class ConcreteClass2(BaseClass):
    def abstract_method(self):
        # This implementation is much larger
        a = 1
        b = 2
        c = 3
        d = 4
        e = 5
        f = 6
        g = 7
        h = 8
        i = 9
        j = 10
        return a + b + c + d + e + f + g + h + i + j
"""
            }
        )
        
        results = self.assert_rule_results(rule, context, 1)
        result = results[0]
        
        self.assertIn("significantly different in size", result.message)
        self.assertIn("abstract_method", result.message)
        self.assertIn("ConcreteClass2", result.message)
        self.assertEqual(result.file_path, "test.py")


if __name__ == "__main__":
    unittest.main()

