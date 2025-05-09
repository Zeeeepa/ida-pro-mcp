"""
PR changes module for the PR static analysis system.

This module provides utilities for extracting and processing PR changes.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ida_pro_mcp.pr_analysis.core.graph_sitter_adapter import GraphSitterAdapter
from ida_pro_mcp.pr_analysis.core.models import AnalysisContext, FileChange

logger = logging.getLogger(__name__)


class PRChangesExtractor:
    """Extracts changes from a PR."""

    def __init__(self, graph_sitter_adapter: GraphSitterAdapter):
        """Initialize the PR changes extractor.

        Args:
            graph_sitter_adapter: The graph-sitter adapter.
        """
        self.graph_sitter_adapter = graph_sitter_adapter

    def extract_changes(
        self,
        repository_path: Path,
        base_commit: str,
        head_commit: str,
        file_paths: Optional[List[Path]] = None,
    ) -> AnalysisContext:
        """Extract changes from a PR.

        Args:
            repository_path: The path to the repository.
            base_commit: The base commit hash.
            head_commit: The head commit hash.
            file_paths: Optional list of file paths to extract changes for.
                If None, all changed files are extracted.

        Returns:
            An analysis context containing the extracted changes.
        """
        # Get the list of changed files
        changed_files = self._get_changed_files(
            repository_path, base_commit, head_commit, file_paths
        )

        # Extract file changes
        file_changes = []
        for file_path, change_type in changed_files:
            try:
                # Get the old and new content of the file
                old_content = self._get_file_content(
                    repository_path, file_path, base_commit
                )
                new_content = self._get_file_content(
                    repository_path, file_path, head_commit
                )

                # Create a file change object
                file_change = self.graph_sitter_adapter.create_file_change(
                    file_path, old_content, new_content
                )
                file_changes.append(file_change)
            except Exception as e:
                logger.error(f"Error extracting changes for file {file_path}: {e}")

        # Create and return the analysis context
        return AnalysisContext(
            file_changes=file_changes,
            repository_path=repository_path,
            base_commit=base_commit,
            head_commit=head_commit,
        )

    def _get_changed_files(
        self,
        repository_path: Path,
        base_commit: str,
        head_commit: str,
        file_paths: Optional[List[Path]] = None,
    ) -> List[Tuple[Path, str]]:
        """Get the list of changed files between two commits.

        Args:
            repository_path: The path to the repository.
            base_commit: The base commit hash.
            head_commit: The head commit hash.
            file_paths: Optional list of file paths to filter by.

        Returns:
            A list of tuples containing the file path and change type.
        """
        # This is a simplified implementation
        # In a real implementation, we would use git to get the list of changed files
        # For now, we'll just return the file_paths if provided
        if file_paths:
            return [(file_path, "modified") for file_path in file_paths]
        return []

    def _get_file_content(
        self, repository_path: Path, file_path: Path, commit: str
    ) -> Optional[str]:
        """Get the content of a file at a specific commit.

        Args:
            repository_path: The path to the repository.
            file_path: The path to the file.
            commit: The commit hash.

        Returns:
            The content of the file, or None if the file doesn't exist.
        """
        # This is a simplified implementation
        # In a real implementation, we would use git to get the file content at a specific commit
        # For now, we'll just read the file from disk if it exists
        full_path = repository_path / file_path
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading file {full_path}: {e}")
        return None

