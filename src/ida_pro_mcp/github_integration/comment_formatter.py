"""
GitHub Comment Formatter for formatting analysis results as GitHub comments.

This module provides a formatter for converting analysis results into
well-formatted GitHub comments with Markdown formatting.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class GitHubCommentFormatter:
    """
    Formatter for converting analysis results into GitHub comments.
    
    This class provides methods for formatting analysis results as
    GitHub comments with Markdown formatting for better readability.
    """
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """
        Format analysis results as a GitHub comment.
        
        Args:
            results: Dictionary containing analysis results
                Expected format:
                {
                    "issues": [
                        {
                            "severity": "error" | "warning" | "info",
                            "message": "Description of the issue",
                            "file": "path/to/file.py",  # optional
                            "line": 42,  # optional
                            "column": 10,  # optional
                            "code": "CODE123"  # optional
                        },
                        ...
                    ],
                    "recommendations": [  # optional
                        "Recommendation 1",
                        "Recommendation 2",
                        ...
                    ],
                    "summary": {  # optional
                        "total_files": 10,
                        "analyzed_files": 8,
                        "execution_time": 1.23
                    }
                }
                
        Returns:
            Formatted comment as a string
        """
        if not results or "issues" not in results:
            return "## PR Static Analysis Results\n\nNo issues found."
        
        # Create comment header
        comment = "## PR Static Analysis Results\n\n"
        
        # Add summary
        comment += "### Summary\n"
        
        # Count issues by severity
        errors = [i for i in results["issues"] if i["severity"] == "error"]
        warnings = [i for i in results["issues"] if i["severity"] == "warning"]
        infos = [i for i in results["issues"] if i["severity"] == "info"]
        
        comment += f"- Total issues: {len(results['issues'])}\n"
        comment += f"- Errors: {len(errors)}\n"
        comment += f"- Warnings: {len(warnings)}\n"
        if infos:
            comment += f"- Info: {len(infos)}\n"
        
        # Add custom summary if provided
        if "summary" in results:
            summary = results["summary"]
            if "total_files" in summary and "analyzed_files" in summary:
                comment += f"- Files analyzed: {summary['analyzed_files']}/{summary['total_files']}\n"
            if "execution_time" in summary:
                comment += f"- Execution time: {summary['execution_time']:.2f}s\n"
        
        # Add details
        if errors:
            comment += "\n### Errors\n"
            for issue in errors:
                comment += self._format_issue(issue)
        
        if warnings:
            comment += "\n### Warnings\n"
            for issue in warnings:
                comment += self._format_issue(issue)
        
        if infos:
            comment += "\n### Info\n"
            for issue in infos:
                comment += self._format_issue(issue)
        
        # Add recommendations
        if results.get("recommendations"):
            comment += "\n### Recommendations\n"
            for rec in results["recommendations"]:
                comment += f"- {rec}\n"
        
        return comment
    
    def _format_issue(self, issue: Dict[str, Any]) -> str:
        """
        Format a single issue as a Markdown list item.
        
        Args:
            issue: Dictionary containing issue data
            
        Returns:
            Formatted issue as a string
        """
        # Start with the issue message
        formatted = f"- **{issue['message']}**"
        
        # Add code if available
        if issue.get("code"):
            formatted = f"- **[{issue['code']}]** {issue['message']}"
        
        # Add file and line information if available
        if issue.get("file"):
            formatted += f" in `{issue['file']}`"
            if issue.get("line"):
                formatted += f" at line {issue['line']}"
                if issue.get("column"):
                    formatted += f", column {issue['column']}"
        
        # Add a newline
        formatted += "\n"
        
        return formatted
    
    def format_error(self, error_message: str) -> str:
        """
        Format an error message as a GitHub comment.
        
        Args:
            error_message: Error message to format
            
        Returns:
            Formatted error message as a string
        """
        return f"## ❌ PR Static Analysis Error\n\n{error_message}\n"
    
    def format_summary(self, results: Dict[str, Any]) -> str:
        """
        Format a summary of the analysis results.
        
        This creates a shorter summary suitable for PR descriptions or
        status messages.
        
        Args:
            results: Dictionary containing analysis results
                
        Returns:
            Formatted summary as a string
        """
        if not results or "issues" not in results:
            return "✅ No issues found"
        
        # Count issues by severity
        errors = len([i for i in results["issues"] if i["severity"] == "error"])
        warnings = len([i for i in results["issues"] if i["severity"] == "warning"])
        infos = len([i for i in results["issues"] if i["severity"] == "info"])
        
        summary = "PR Static Analysis: "
        
        if errors > 0:
            summary += f"❌ {errors} error{'s' if errors > 1 else ''}"
            if warnings > 0:
                summary += f", ⚠️ {warnings} warning{'s' if warnings > 1 else ''}"
        elif warnings > 0:
            summary += f"⚠️ {warnings} warning{'s' if warnings > 1 else ''}"
        else:
            summary += f"✅ {infos} info item{'s' if infos > 1 else ''}"
        
        return summary

