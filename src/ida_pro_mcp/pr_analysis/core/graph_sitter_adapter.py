"""
Adapter for graph-sitter's codebase representation.

This module provides adapter classes to work with graph-sitter's CodebaseContext
and utilities for traversing the code graph.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from ida_pro_mcp.pr_analysis.core.models import (
    CodeElement,
    CodeElementType,
    FileChange,
    Location,
)

logger = logging.getLogger(__name__)


class GraphSitterAdapter:
    """Adapter for graph-sitter's CodebaseContext."""

    def __init__(self, codebase_context: Any):
        """Initialize the adapter.

        Args:
            codebase_context: The graph-sitter CodebaseContext instance.
        """
        self.codebase_context = codebase_context

    def get_file_elements(self, file_path: Path) -> List[CodeElement]:
        """Get all code elements in a file.

        Args:
            file_path: The path to the file.

        Returns:
            A list of code elements in the file.
        """
        elements = []
        try:
            # Get the file from the codebase context
            file = self.codebase_context.get_file(file_path)
            if not file:
                logger.warning(f"File not found in codebase context: {file_path}")
                return elements

            # Create a code element for the file itself
            file_element = self._create_file_element(file)
            elements.append(file_element)

            # Add all code elements in the file
            elements.extend(self._extract_elements_from_file(file, file_element))

        except Exception as e:
            logger.error(f"Error getting code elements for file {file_path}: {e}")

        return elements

    def _create_file_element(self, file: Any) -> CodeElement:
        """Create a CodeElement for a file.

        Args:
            file: The graph-sitter file object.

        Returns:
            A CodeElement representing the file.
        """
        file_path = Path(file.path)
        location = Location(
            file_path=file_path,
            line=1,
            column=1,
            end_line=None,  # We don't know the end line yet
            end_column=None,
        )

        # Determine the language from the file extension
        language = self._get_language_from_file(file)

        return CodeElement(
            element_type=CodeElementType.FILE,
            name=file_path.name,
            location=location,
            language=language,
            content="",  # We'll set this later if needed
            parent=None,
            children=[],
            metadata={"node_id": getattr(file, "node_id", None)},
        )

    def _extract_elements_from_file(
        self, file: Any, parent_element: CodeElement
    ) -> List[CodeElement]:
        """Extract all code elements from a file.

        Args:
            file: The graph-sitter file object.
            parent_element: The parent CodeElement (the file element).

        Returns:
            A list of CodeElements representing the code elements in the file.
        """
        elements = []

        # Extract classes
        for cls in self._get_classes(file):
            class_element = self._create_class_element(cls, parent_element)
            elements.append(class_element)

            # Extract methods
            for method in self._get_methods(cls):
                method_element = self._create_method_element(method, class_element)
                elements.append(method_element)

        # Extract functions (not methods)
        for func in self._get_functions(file):
            func_element = self._create_function_element(func, parent_element)
            elements.append(func_element)

        # Extract imports
        for imp in self._get_imports(file):
            import_element = self._create_import_element(imp, parent_element)
            elements.append(import_element)

        # Extract variables
        for var in self._get_variables(file):
            var_element = self._create_variable_element(var, parent_element)
            elements.append(var_element)

        return elements

    def _get_language_from_file(self, file: Any) -> str:
        """Get the programming language of a file.

        Args:
            file: The graph-sitter file object.

        Returns:
            The programming language as a string.
        """
        # Try to get the language from the file object
        if hasattr(file, "language"):
            return str(file.language)

        # Fall back to determining language from file extension
        file_path = Path(file.path)
        extension = file_path.suffix.lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".rs": "rust",
        }

        return language_map.get(extension, "unknown")

    def _get_classes(self, file: Any) -> List[Any]:
        """Get all classes in a file.

        Args:
            file: The graph-sitter file object.

        Returns:
            A list of class objects.
        """
        try:
            if hasattr(file, "classes"):
                return file.classes
            return []
        except Exception as e:
            logger.error(f"Error getting classes for file {file.path}: {e}")
            return []

    def _get_methods(self, cls: Any) -> List[Any]:
        """Get all methods in a class.

        Args:
            cls: The graph-sitter class object.

        Returns:
            A list of method objects.
        """
        try:
            if hasattr(cls, "methods"):
                return cls.methods
            return []
        except Exception as e:
            logger.error(f"Error getting methods for class {cls.name}: {e}")
            return []

    def _get_functions(self, file: Any) -> List[Any]:
        """Get all functions in a file (not methods).

        Args:
            file: The graph-sitter file object.

        Returns:
            A list of function objects.
        """
        try:
            if hasattr(file, "functions"):
                return file.functions
            return []
        except Exception as e:
            logger.error(f"Error getting functions for file {file.path}: {e}")
            return []

    def _get_imports(self, file: Any) -> List[Any]:
        """Get all imports in a file.

        Args:
            file: The graph-sitter file object.

        Returns:
            A list of import objects.
        """
        try:
            if hasattr(file, "imports"):
                return file.imports
            return []
        except Exception as e:
            logger.error(f"Error getting imports for file {file.path}: {e}")
            return []

    def _get_variables(self, file: Any) -> List[Any]:
        """Get all variables in a file.

        Args:
            file: The graph-sitter file object.

        Returns:
            A list of variable objects.
        """
        try:
            if hasattr(file, "variables"):
                return file.variables
            return []
        except Exception as e:
            logger.error(f"Error getting variables for file {file.path}: {e}")
            return []

    def _create_class_element(self, cls: Any, parent_element: CodeElement) -> CodeElement:
        """Create a CodeElement for a class.

        Args:
            cls: The graph-sitter class object.
            parent_element: The parent CodeElement.

        Returns:
            A CodeElement representing the class.
        """
        location = self._get_location_from_node(cls, parent_element.file_path)
        
        element = CodeElement(
            element_type=CodeElementType.CLASS,
            name=cls.name,
            location=location,
            language=parent_element.language,
            content=self._get_node_content(cls),
            parent=parent_element,
            children=[],
            metadata={"node_id": getattr(cls, "node_id", None)},
        )
        
        parent_element.children.append(element)
        return element

    def _create_method_element(self, method: Any, parent_element: CodeElement) -> CodeElement:
        """Create a CodeElement for a method.

        Args:
            method: The graph-sitter method object.
            parent_element: The parent CodeElement.

        Returns:
            A CodeElement representing the method.
        """
        location = self._get_location_from_node(method, parent_element.location.file_path)
        
        element = CodeElement(
            element_type=CodeElementType.METHOD,
            name=method.name,
            location=location,
            language=parent_element.language,
            content=self._get_node_content(method),
            parent=parent_element,
            children=[],
            metadata={"node_id": getattr(method, "node_id", None)},
        )
        
        parent_element.children.append(element)
        return element

    def _create_function_element(self, func: Any, parent_element: CodeElement) -> CodeElement:
        """Create a CodeElement for a function.

        Args:
            func: The graph-sitter function object.
            parent_element: The parent CodeElement.

        Returns:
            A CodeElement representing the function.
        """
        location = self._get_location_from_node(func, parent_element.location.file_path)
        
        element = CodeElement(
            element_type=CodeElementType.FUNCTION,
            name=func.name,
            location=location,
            language=parent_element.language,
            content=self._get_node_content(func),
            parent=parent_element,
            children=[],
            metadata={"node_id": getattr(func, "node_id", None)},
        )
        
        parent_element.children.append(element)
        return element

    def _create_import_element(self, imp: Any, parent_element: CodeElement) -> CodeElement:
        """Create a CodeElement for an import.

        Args:
            imp: The graph-sitter import object.
            parent_element: The parent CodeElement.

        Returns:
            A CodeElement representing the import.
        """
        location = self._get_location_from_node(imp, parent_element.location.file_path)
        
        element = CodeElement(
            element_type=CodeElementType.IMPORT,
            name=getattr(imp, "name", str(imp)),
            location=location,
            language=parent_element.language,
            content=self._get_node_content(imp),
            parent=parent_element,
            children=[],
            metadata={"node_id": getattr(imp, "node_id", None)},
        )
        
        parent_element.children.append(element)
        return element

    def _create_variable_element(self, var: Any, parent_element: CodeElement) -> CodeElement:
        """Create a CodeElement for a variable.

        Args:
            var: The graph-sitter variable object.
            parent_element: The parent CodeElement.

        Returns:
            A CodeElement representing the variable.
        """
        location = self._get_location_from_node(var, parent_element.location.file_path)
        
        element = CodeElement(
            element_type=CodeElementType.VARIABLE,
            name=var.name,
            location=location,
            language=parent_element.language,
            content=self._get_node_content(var),
            parent=parent_element,
            children=[],
            metadata={"node_id": getattr(var, "node_id", None)},
        )
        
        parent_element.children.append(element)
        return element

    def _get_location_from_node(self, node: Any, file_path: Path) -> Location:
        """Get the location of a node.

        Args:
            node: The graph-sitter node object.
            file_path: The path to the file containing the node.

        Returns:
            A Location object representing the node's location.
        """
        line = getattr(node, "line", 1)
        column = getattr(node, "column", 1)
        end_line = getattr(node, "end_line", None)
        end_column = getattr(node, "end_column", None)
        
        return Location(
            file_path=file_path,
            line=line,
            column=column,
            end_line=end_line,
            end_column=end_column,
        )

    def _get_node_content(self, node: Any) -> str:
        """Get the content of a node.

        Args:
            node: The graph-sitter node object.

        Returns:
            The content of the node as a string.
        """
        if hasattr(node, "content"):
            return node.content
        if hasattr(node, "source"):
            return node.source
        return ""

    def create_file_change(
        self, file_path: Path, old_content: Optional[str], new_content: Optional[str]
    ) -> FileChange:
        """Create a FileChange object for a file.

        Args:
            file_path: The path to the file.
            old_content: The old content of the file.
            new_content: The new content of the file.

        Returns:
            A FileChange object representing the change to the file.
        """
        is_new = old_content is None and new_content is not None
        is_deleted = old_content is not None and new_content is None
        
        # Determine the language from the file extension
        language = self._get_language_from_extension(file_path)
        
        # Get code elements if the file exists in the new version
        elements = []
        if new_content is not None:
            elements = self.get_file_elements(file_path)
        
        return FileChange(
            file_path=file_path,
            language=language,
            old_content=old_content,
            new_content=new_content,
            is_new=is_new,
            is_deleted=is_deleted,
            is_renamed=False,  # We don't have this information yet
            old_file_path=None,  # We don't have this information yet
            diff=None,  # We don't have this information yet
            elements=elements,
        )

    def _get_language_from_extension(self, file_path: Path) -> str:
        """Get the programming language from a file extension.

        Args:
            file_path: The path to the file.

        Returns:
            The programming language as a string.
        """
        extension = file_path.suffix.lower()
        
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".rs": "rust",
        }
        
        return language_map.get(extension, "unknown")

