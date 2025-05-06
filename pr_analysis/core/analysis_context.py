"""
Analysis context for PR static analysis.

This module provides the PRAnalysisContext class which holds the state during analysis.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import os
import json
from datetime import datetime


class AnalysisStatus(Enum):
    """Status of the analysis process."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FileChange:
    """Represents a file change in a PR."""
    filename: str
    status: str  # "added", "modified", "removed"
    patch: Optional[str] = None
    changed_lines: List[int] = field(default_factory=list)
    
    def is_code_file(self) -> bool:
        """Check if this is a code file based on extension."""
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.rb'}
        _, ext = os.path.splitext(self.filename)
        return ext.lower() in code_extensions


@dataclass
class AnalysisResult:
    """Result of a single rule analysis."""
    rule_id: str
    rule_name: str
    severity: str  # "error", "warning", "info"
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    suggested_fix: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PRAnalysisContext:
    """
    Context for PR analysis that holds the state during analysis.
    
    This class provides methods to access PR data, codebase snapshots, and analysis results.
    It also includes utilities for tracking analysis progress.
    """
    
    def __init__(self, pr_id: str, repo_name: str, base_branch: str, head_branch: str):
        """
        Initialize a new PR analysis context.
        
        Args:
            pr_id: The ID of the PR being analyzed
            repo_name: The name of the repository
            base_branch: The base branch of the PR
            head_branch: The head branch of the PR
        """
        self.pr_id = pr_id
        self.repo_name = repo_name
        self.base_branch = base_branch
        self.head_branch = head_branch
        self.file_changes: Dict[str, FileChange] = {}
        self.results: List[AnalysisResult] = []
        self.status = AnalysisStatus.NOT_STARTED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
        self.processed_rules: Set[str] = set()
        self.failed_rules: Set[str] = set()
        
    def add_file_change(self, file_change: FileChange) -> None:
        """
        Add a file change to the context.
        
        Args:
            file_change: The file change to add
        """
        self.file_changes[file_change.filename] = file_change
        
    def add_result(self, result: AnalysisResult) -> None:
        """
        Add an analysis result to the context.
        
        Args:
            result: The analysis result to add
        """
        self.results.append(result)
        
    def start_analysis(self) -> None:
        """Mark the analysis as started."""
        self.status = AnalysisStatus.IN_PROGRESS
        self.start_time = datetime.now()
        
    def complete_analysis(self) -> None:
        """Mark the analysis as completed."""
        self.status = AnalysisStatus.COMPLETED
        self.end_time = datetime.now()
        
    def fail_analysis(self) -> None:
        """Mark the analysis as failed."""
        self.status = AnalysisStatus.FAILED
        self.end_time = datetime.now()
        
    def mark_rule_processed(self, rule_id: str) -> None:
        """
        Mark a rule as processed.
        
        Args:
            rule_id: The ID of the rule
        """
        self.processed_rules.add(rule_id)
        
    def mark_rule_failed(self, rule_id: str) -> None:
        """
        Mark a rule as failed.
        
        Args:
            rule_id: The ID of the rule
        """
        self.failed_rules.add(rule_id)
        self.processed_rules.add(rule_id)
        
    def get_code_files(self) -> List[FileChange]:
        """
        Get all code files that were changed in the PR.
        
        Returns:
            A list of FileChange objects representing code files
        """
        return [fc for fc in self.file_changes.values() if fc.is_code_file()]
        
    def get_results_by_severity(self, severity: str) -> List[AnalysisResult]:
        """
        Get all results with the specified severity.
        
        Args:
            severity: The severity to filter by ("error", "warning", "info")
            
        Returns:
            A list of AnalysisResult objects with the specified severity
        """
        return [r for r in self.results if r.severity == severity]
        
    def get_results_by_file(self, filename: str) -> List[AnalysisResult]:
        """
        Get all results for the specified file.
        
        Args:
            filename: The filename to filter by
            
        Returns:
            A list of AnalysisResult objects for the specified file
        """
        return [r for r in self.results if r.file == filename]
        
    def get_analysis_duration(self) -> Optional[float]:
        """
        Get the duration of the analysis in seconds.
        
        Returns:
            The duration in seconds, or None if the analysis is not complete
        """
        if self.start_time is None or self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds()
        
    def get_progress(self) -> float:
        """
        Get the progress of the analysis as a percentage.
        
        Returns:
            The progress as a percentage (0-100)
        """
        if self.status == AnalysisStatus.NOT_STARTED:
            return 0.0
        if self.status in (AnalysisStatus.COMPLETED, AnalysisStatus.FAILED):
            return 100.0
        
        # If we have metadata about total rules, use that for progress calculation
        total_rules = self.metadata.get("total_rules", 0)
        if total_rules > 0:
            return (len(self.processed_rules) / total_rules) * 100.0
            
        # Otherwise, use a simple heuristic based on file changes
        if not self.file_changes:
            return 0.0
        
        # Assume each file gets analyzed by at least one rule
        return (len(self.processed_rules) / len(self.file_changes)) * 100.0
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary.
        
        Returns:
            A dictionary representation of the context
        """
        return {
            "pr_id": self.pr_id,
            "repo_name": self.repo_name,
            "base_branch": self.base_branch,
            "head_branch": self.head_branch,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "file_changes": {k: vars(v) for k, v in self.file_changes.items()},
            "results": [vars(r) for r in self.results],
            "metadata": self.metadata,
            "processed_rules": list(self.processed_rules),
            "failed_rules": list(self.failed_rules),
        }
        
    def save_to_file(self, filename: str) -> None:
        """
        Save the context to a file.
        
        Args:
            filename: The filename to save to
        """
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, filename: str) -> "PRAnalysisContext":
        """
        Load a context from a file.
        
        Args:
            filename: The filename to load from
            
        Returns:
            A PRAnalysisContext object
        """
        with open(filename, "r") as f:
            data = json.load(f)
            
        context = cls(
            pr_id=data["pr_id"],
            repo_name=data["repo_name"],
            base_branch=data["base_branch"],
            head_branch=data["head_branch"],
        )
        
        context.status = AnalysisStatus(data["status"])
        context.start_time = datetime.fromisoformat(data["start_time"]) if data["start_time"] else None
        context.end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
        
        for filename, fc_data in data["file_changes"].items():
            file_change = FileChange(
                filename=fc_data["filename"],
                status=fc_data["status"],
                patch=fc_data.get("patch"),
                changed_lines=fc_data.get("changed_lines", []),
            )
            context.file_changes[filename] = file_change
            
        for result_data in data["results"]:
            result = AnalysisResult(
                rule_id=result_data["rule_id"],
                rule_name=result_data["rule_name"],
                severity=result_data["severity"],
                message=result_data["message"],
                file=result_data.get("file"),
                line=result_data.get("line"),
                column=result_data.get("column"),
                suggested_fix=result_data.get("suggested_fix"),
                metadata=result_data.get("metadata", {}),
            )
            context.results.append(result)
            
        context.metadata = data.get("metadata", {})
        context.processed_rules = set(data.get("processed_rules", []))
        context.failed_rules = set(data.get("failed_rules", []))
        
        return context

