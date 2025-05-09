"""
Implementation validation rules for the PR static analysis system.

This module contains rules for detecting implementation issues, such as
missing implementations, incorrect implementations, and inconsistent implementations.
"""
import re
import ast
from typing import List, Dict, Any, Optional, Set, Tuple

from ..core import BaseRule, AnalysisResult, AnalysisContext


class MissingImplementationRule(BaseRule):
    """
    Rule for detecting missing implementations.
    """
    def __init__(self):
        """Initialize the missing implementation rule."""
        super().__init__(
            name="missing_implementation",
            description="Detects missing implementations",
            severity="error"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect missing implementations.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in context.get_changed_files():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            
            try:
                # Parse the file into an AST
                tree = ast.parse(content)
                
                # Find all abstract methods and their implementations
                abstract_methods = set()
                implemented_methods = set()
                
                # Find all classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if this class inherits from ABC
                        is_abstract = False
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id == 'ABC':
                                is_abstract = True
                                break
                            elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name) and base.value.id == 'abc' and base.attr == 'ABC':
                                is_abstract = True
                                break
                        
                        # Find abstract methods in this class
                        class_name = node.name
                        for method in node.body:
                            if isinstance(method, ast.FunctionDef):
                                method_name = method.name
                                
                                # Check if this method is abstract
                                for decorator in method.decorator_list:
                                    if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                                        abstract_methods.add(f"{class_name}.{method_name}")
                                        break
                                    elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name) and decorator.value.id == 'abc' and decorator.attr == 'abstractmethod':
                                        abstract_methods.add(f"{class_name}.{method_name}")
                                        break
                                
                                # If not abstract, add to implemented methods
                                if f"{class_name}.{method_name}" not in abstract_methods:
                                    implemented_methods.add(f"{class_name}.{method_name}")
                
                # Find all subclasses and their implementations
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if this class inherits from any other class
                        for base in node.bases:
                            base_name = None
                            if isinstance(base, ast.Name):
                                base_name = base.id
                            
                            if base_name:
                                # Find all methods in this class
                                class_name = node.name
                                for method in node.body:
                                    if isinstance(method, ast.FunctionDef):
                                        method_name = method.name
                                        implemented_methods.add(f"{class_name}.{method_name}")
                                        
                                        # Check if this method overrides an abstract method
                                        if f"{base_name}.{method_name}" in abstract_methods:
                                            implemented_methods.add(f"{base_name}.{method_name}")
                
                # Check for missing implementations
                missing_implementations = abstract_methods - implemented_methods
                for method in missing_implementations:
                    class_name, method_name = method.split('.')
                    
                    # Find the line number of the class definition
                    line_number = None
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == class_name:
                            line_number = node.lineno
                            break
                    
                    results.append(AnalysisResult(
                        rule_name=self.name,
                        message=f"Abstract method '{method_name}' in class '{class_name}' is not implemented",
                        file_path=file_path,
                        line_number=line_number,
                        severity=self.severity
                    ))
            
            except SyntaxError:
                # If the file has syntax errors, we can't parse it
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains syntax errors, cannot analyze implementations",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        return results


class IncorrectImplementationRule(BaseRule):
    """
    Rule for detecting incorrect implementations.
    """
    def __init__(self):
        """Initialize the incorrect implementation rule."""
        super().__init__(
            name="incorrect_implementation",
            description="Detects incorrect implementations",
            severity="error"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect incorrect implementations.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in context.get_changed_files():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            
            try:
                # Parse the file into an AST
                tree = ast.parse(content)
                
                # Find all method signatures
                method_signatures: Dict[str, Dict[str, List[ast.FunctionDef]]] = {}
                
                # Find all classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        
                        # Find all methods in this class
                        for method in node.body:
                            if isinstance(method, ast.FunctionDef):
                                method_name = method.name
                                
                                # Skip private methods
                                if method_name.startswith('_') and not method_name.startswith('__'):
                                    continue
                                
                                # Add to method signatures
                                if method_name not in method_signatures:
                                    method_signatures[method_name] = {}
                                
                                if class_name not in method_signatures[method_name]:
                                    method_signatures[method_name][class_name] = []
                                
                                method_signatures[method_name][class_name].append(method)
                
                # Check for incorrect implementations
                for method_name, class_methods in method_signatures.items():
                    if len(class_methods) <= 1:
                        continue  # Only one class implements this method, no inconsistency
                    
                    # Get all parameter lists
                    param_lists = {}
                    for class_name, methods in class_methods.items():
                        for method in methods:
                            param_list = []
                            for arg in method.args.args:
                                # Skip self and cls
                                if arg.arg in ('self', 'cls'):
                                    continue
                                
                                param_list.append(arg.arg)
                            
                            param_lists[class_name] = param_list
                    
                    # Check if all implementations have compatible parameter lists
                    base_classes = []
                    derived_classes = []
                    
                    # Identify base and derived classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            
                            if class_name not in param_lists:
                                continue
                            
                            # Check if this class is a base class for any other class
                            is_base = False
                            for other_node in ast.walk(tree):
                                if isinstance(other_node, ast.ClassDef) and other_node.name != class_name:
                                    for base in other_node.bases:
                                        if isinstance(base, ast.Name) and base.id == class_name:
                                            is_base = True
                                            break
                            
                            if is_base:
                                base_classes.append(class_name)
                            else:
                                derived_classes.append(class_name)
                    
                    # Check if derived class implementations are compatible with base class implementations
                    for base_class in base_classes:
                        base_params = param_lists.get(base_class, [])
                        
                        for derived_class in derived_classes:
                            derived_params = param_lists.get(derived_class, [])
                            
                            # Check if the derived class implementation is compatible with the base class
                            if len(derived_params) != len(base_params):
                                # Find the line number of the method definition
                                line_number = None
                                for node in ast.walk(tree):
                                    if isinstance(node, ast.ClassDef) and node.name == derived_class:
                                        for method in node.body:
                                            if isinstance(method, ast.FunctionDef) and method.name == method_name:
                                                line_number = method.lineno
                                                break
                                
                                results.append(AnalysisResult(
                                    rule_name=self.name,
                                    message=f"Method '{method_name}' in class '{derived_class}' has a different number of parameters than in base class '{base_class}'",
                                    file_path=file_path,
                                    line_number=line_number,
                                    severity=self.severity
                                ))
                                continue
                            
                            # Check if parameter names match
                            for i, (base_param, derived_param) in enumerate(zip(base_params, derived_params)):
                                if base_param != derived_param:
                                    # Find the line number of the method definition
                                    line_number = None
                                    for node in ast.walk(tree):
                                        if isinstance(node, ast.ClassDef) and node.name == derived_class:
                                            for method in node.body:
                                                if isinstance(method, ast.FunctionDef) and method.name == method_name:
                                                    line_number = method.lineno
                                                    break
                                    
                                    results.append(AnalysisResult(
                                        rule_name=self.name,
                                        message=f"Method '{method_name}' in class '{derived_class}' has a different parameter name at position {i+1} than in base class '{base_class}': '{derived_param}' vs '{base_param}'",
                                        file_path=file_path,
                                        line_number=line_number,
                                        severity=self.severity
                                    ))
            
            except SyntaxError:
                # If the file has syntax errors, we can't parse it
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains syntax errors, cannot analyze implementations",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        return results


class InconsistentImplementationRule(BaseRule):
    """
    Rule for detecting inconsistent implementations.
    """
    def __init__(self):
        """Initialize the inconsistent implementation rule."""
        super().__init__(
            name="inconsistent_implementation",
            description="Detects inconsistent implementations",
            severity="warning"
        )

    def run(self, context: AnalysisContext) -> List[AnalysisResult]:
        """
        Run the rule to detect inconsistent implementations.

        Args:
            context: Analysis context containing PR data and other information

        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in context.get_changed_files():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            content = context.get_file_content(file_path)
            
            try:
                # Parse the file into an AST
                tree = ast.parse(content)
                
                # Find all interface-like classes
                interface_classes = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if this class has abstract methods
                        has_abstract_methods = False
                        for method in node.body:
                            if isinstance(method, ast.FunctionDef):
                                for decorator in method.decorator_list:
                                    if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                                        has_abstract_methods = True
                                        break
                                    elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name) and decorator.value.id == 'abc' and decorator.attr == 'abstractmethod':
                                        has_abstract_methods = True
                                        break
                        
                        if has_abstract_methods:
                            interface_classes.append(node.name)
                
                # Find all implementations of interface methods
                for interface_class in interface_classes:
                    # Find all abstract methods in this interface
                    abstract_methods = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == interface_class:
                            for method in node.body:
                                if isinstance(method, ast.FunctionDef):
                                    for decorator in method.decorator_list:
                                        if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                                            abstract_methods.append(method.name)
                                            break
                                        elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name) and decorator.value.id == 'abc' and decorator.attr == 'abstractmethod':
                                            abstract_methods.append(method.name)
                                            break
                    
                    # Find all implementations of these methods
                    implementations: Dict[str, List[Tuple[str, ast.FunctionDef]]] = {}
                    for method_name in abstract_methods:
                        implementations[method_name] = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name != interface_class:
                            # Check if this class implements the interface
                            implements_interface = False
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id == interface_class:
                                    implements_interface = True
                                    break
                            
                            if implements_interface:
                                # Find implementations of abstract methods
                                for method in node.body:
                                    if isinstance(method, ast.FunctionDef) and method.name in abstract_methods:
                                        implementations[method.name].append((node.name, method))
                    
                    # Check for inconsistent implementations
                    for method_name, impls in implementations.items():
                        if len(impls) <= 1:
                            continue  # Only one implementation, no inconsistency
                        
                        # Check if all implementations have similar structure
                        # This is a simplified check and might produce false positives/negatives
                        first_class, first_impl = impls[0]
                        first_body_len = len(first_impl.body)
                        
                        for class_name, impl in impls[1:]:
                            body_len = len(impl.body)
                            
                            # Check if the implementation is significantly different in size
                            if abs(body_len - first_body_len) > max(3, first_body_len * 0.5):
                                results.append(AnalysisResult(
                                    rule_name=self.name,
                                    message=f"Implementation of method '{method_name}' in class '{class_name}' is significantly different in size from implementation in class '{first_class}'",
                                    file_path=file_path,
                                    line_number=impl.lineno,
                                    severity=self.severity
                                ))
            
            except SyntaxError:
                # If the file has syntax errors, we can't parse it
                results.append(AnalysisResult(
                    rule_name=self.name,
                    message="File contains syntax errors, cannot analyze implementations",
                    file_path=file_path,
                    severity=self.severity
                ))
        
        return results

