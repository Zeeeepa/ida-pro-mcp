"""
Comment formatter for GitHub comments.

This module provides a formatter for GitHub comments.
"""

from typing import List, Dict, Any
import textwrap

from ..core.analysis_context import AnalysisResult


class CommentFormatter:
    """
    Formatter for GitHub comments.
    
    This class provides methods for formatting analysis results as GitHub comments.
    """
    
    def __init__(self):
        """Initialize a new comment formatter."""
        self.severity_icons = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
        }
        
    def format_results(self, results: List[AnalysisResult]) -> str:
        """
        Format analysis results as a GitHub comment.
        
        Args:
            results: The analysis results to format
            
        Returns:
            A formatted comment
        """
        if not results:
            return ""
            
        # Group results by file
        results_by_file: Dict[str, List[AnalysisResult]] = {}
        for result in results:
            file = result.file or "General"
            if file not in results_by_file:
                results_by_file[file] = []
            results_by_file[file].append(result)
            
        # Format comment
        comment = "# PR Analysis Results\n\n"
        
        # Add summary
        errors = len([r for r in results if r.severity == "error"])
        warnings = len([r for r in results if r.severity == "warning"])
        infos = len([r for r in results if r.severity == "info"])
        
        comment += "## Summary\n\n"
        comment += f"- {self.severity_icons['error']} Errors: {errors}\n"
        comment += f"- {self.severity_icons['warning']} Warnings: {warnings}\n"
        comment += f"- {self.severity_icons['info']} Info: {infos}\n\n"
        
        # Add results by file
        for file, file_results in results_by_file.items():
            if file == "General":
                comment += "## General Issues\n\n"
            else:
                comment += f"## File: `{file}`\n\n"
                
            for result in file_results:
                icon = self.severity_icons.get(result.severity, "")
                location = f"line {result.line}" if result.line else ""
                
                comment += f"### {icon} {result.rule_name} {location}\n\n"
                comment += f"{result.message}\n\n"
                
                if result.suggested_fix:
                    comment += "**Suggested Fix:**\n\n"
                    comment += f"```\n{result.suggested_fix}\n```\n\n"
                    
        return comment
        
    def format_result_as_review_comment(self, result: AnalysisResult) -> str:
        """
        Format a single analysis result as a GitHub review comment.
        
        Args:
            result: The analysis result to format
            
        Returns:
            A formatted comment
        """
        icon = self.severity_icons.get(result.severity, "")
        comment = f"{icon} **{result.rule_name}**\n\n{result.message}\n"
        
        if result.suggested_fix:
            comment += f"\n**Suggested Fix:**\n\n```\n{result.suggested_fix}\n```"
            
        return comment
        
    def format_summary_as_review(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Format a summary of analysis results as a GitHub review.
        
        Args:
            results: The analysis results to format
            
        Returns:
            A dictionary with the review data
        """
        if not results:
            return {
                "body": "No issues found!",
                "event": "APPROVE",
                "comments": [],
            }
            
        # Count issues by severity
        errors = len([r for r in results if r.severity == "error"])
        warnings = len([r for r in results if r.severity == "warning"])
        infos = len([r for r in results if r.severity == "info"])
        
        # Determine review event
        event = "APPROVE"
        if errors > 0:
            event = "REQUEST_CHANGES"
        elif warnings > 0:
            event = "COMMENT"
            
        # Format review body
        body = "# PR Analysis Results\n\n"
        body += "## Summary\n\n"
        body += f"- {self.severity_icons['error']} Errors: {errors}\n"
        body += f"- {self.severity_icons['warning']} Warnings: {warnings}\n"
        body += f"- {self.severity_icons['info']} Info: {infos}\n\n"
        
        if errors > 0:
            body += "Please fix the errors before merging.\n"
        elif warnings > 0:
            body += "Please consider addressing the warnings.\n"
            
        # Format review comments
        comments = []
        for result in results:
            if result.file and result.line:
                comments.append({
                    "path": result.file,
                    "position": result.line,
                    "body": self.format_result_as_review_comment(result),
                })
                
        return {
            "body": body,
            "event": event,
            "comments": comments,
        }

