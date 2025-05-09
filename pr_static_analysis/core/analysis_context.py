"""
Analysis Context Module

This module provides the PRAnalysisContext class which holds the state during PR analysis.
It provides methods to access PR data, codebase snapshots, and analysis results.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Represents the result of a single rule analysis."""
    rule_id: str
    status: str  # 'pass', 'fail', 'warning', 'error'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PRData:
    """Represents the pull request data."""
    pr_id: str
    title: str
    description: str
    author: str
    base_branch: str
    head_branch: str
    created_at: datetime
    updated_at: datetime
    files_changed: List[str] = field(default_factory=list)
    diff_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class PRAnalysisContext:
    """
    Holds the state during PR analysis.
    
    This class provides methods to access PR data, codebase snapshots, and analysis results.
    It also provides utilities for tracking analysis progress.
    """
    
    def __init__(self, pr_data: PRData):
        """
        Initialize the PR analysis context.
        
        Args:
            pr_data: The pull request data.
        """
        self.pr_data = pr_data
        self.results: List[AnalysisResult] = []
        self._base_snapshot_path: Optional[str] = None
        self._head_snapshot_path: Optional[str] = None
        self._analysis_start_time = datetime.now()
        self._analysis_end_time: Optional[datetime] = None
        self._progress: Dict[str, Any] = {
            "total_rules": 0,
            "completed_rules": 0,
            "current_rule": None,
            "status": "initialized"
        }
        
    def set_base_snapshot_path(self, path: str) -> None:
        """
        Set the path to the base branch snapshot.
        
        Args:
            path: The path to the base branch snapshot.
        """
        if not os.path.exists(path):
            raise ValueError(f"Base snapshot path does not exist: {path}")
        self._base_snapshot_path = path
        
    def set_head_snapshot_path(self, path: str) -> None:
        """
        Set the path to the head branch snapshot.
        
        Args:
            path: The path to the head branch snapshot.
        """
        if not os.path.exists(path):
            raise ValueError(f"Head snapshot path does not exist: {path}")
        self._head_snapshot_path = path
        
    def get_base_snapshot_path(self) -> Optional[str]:
        """
        Get the path to the base branch snapshot.
        
        Returns:
            The path to the base branch snapshot.
        """
        return self._base_snapshot_path
        
    def get_head_snapshot_path(self) -> Optional[str]:
        """
        Get the path to the head branch snapshot.
        
        Returns:
            The path to the head branch snapshot.
        """
        return self._head_snapshot_path
        
    def add_result(self, result: AnalysisResult) -> None:
        """
        Add an analysis result.
        
        Args:
            result: The analysis result to add.
        """
        self.results.append(result)
        
    def get_results(self) -> List[AnalysisResult]:
        """
        Get all analysis results.
        
        Returns:
            A list of all analysis results.
        """
        return self.results
        
    def get_results_by_status(self, status: str) -> List[AnalysisResult]:
        """
        Get analysis results by status.
        
        Args:
            status: The status to filter by ('pass', 'fail', 'warning', 'error').
            
        Returns:
            A list of analysis results with the specified status.
        """
        return [r for r in self.results if r.status == status]
        
    def get_results_by_rule(self, rule_id: str) -> List[AnalysisResult]:
        """
        Get analysis results by rule ID.
        
        Args:
            rule_id: The rule ID to filter by.
            
        Returns:
            A list of analysis results for the specified rule.
        """
        return [r for r in self.results if r.rule_id == rule_id]
        
    def get_file_content_base(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file from the base branch snapshot.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The content of the file, or None if the file does not exist.
        """
        if not self._base_snapshot_path:
            raise ValueError("Base snapshot path not set")
            
        full_path = os.path.join(self._base_snapshot_path, file_path)
        if not os.path.exists(full_path):
            return None
            
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def get_file_content_head(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file from the head branch snapshot.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The content of the file, or None if the file does not exist.
        """
        if not self._head_snapshot_path:
            raise ValueError("Head snapshot path not set")
            
        full_path = os.path.join(self._head_snapshot_path, file_path)
        if not os.path.exists(full_path):
            return None
            
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def start_analysis(self, total_rules: int) -> None:
        """
        Start the analysis process.
        
        Args:
            total_rules: The total number of rules to be executed.
        """
        self._analysis_start_time = datetime.now()
        self._progress["total_rules"] = total_rules
        self._progress["completed_rules"] = 0
        self._progress["status"] = "running"
        logger.info(f"Starting analysis of PR {self.pr_data.pr_id} with {total_rules} rules")
        
    def complete_rule(self, rule_id: str) -> None:
        """
        Mark a rule as completed.
        
        Args:
            rule_id: The ID of the completed rule.
        """
        self._progress["completed_rules"] += 1
        self._progress["current_rule"] = None
        logger.debug(f"Completed rule {rule_id}. Progress: {self._progress['completed_rules']}/{self._progress['total_rules']}")
        
    def start_rule(self, rule_id: str) -> None:
        """
        Mark a rule as started.
        
        Args:
            rule_id: The ID of the rule being started.
        """
        self._progress["current_rule"] = rule_id
        logger.debug(f"Starting rule {rule_id}")
        
    def complete_analysis(self) -> None:
        """Complete the analysis process."""
        self._analysis_end_time = datetime.now()
        self._progress["status"] = "completed"
        duration = self._analysis_end_time - self._analysis_start_time
        logger.info(f"Completed analysis of PR {self.pr_data.pr_id} in {duration.total_seconds():.2f} seconds")
        
    def get_progress(self) -> Dict[str, Any]:
        """
        Get the current progress of the analysis.
        
        Returns:
            A dictionary containing progress information.
        """
        return self._progress
        
    def get_analysis_duration(self) -> Optional[float]:
        """
        Get the duration of the analysis in seconds.
        
        Returns:
            The duration of the analysis in seconds, or None if the analysis is not complete.
        """
        if not self._analysis_end_time:
            return None
            
        duration = self._analysis_end_time - self._analysis_start_time
        return duration.total_seconds()

