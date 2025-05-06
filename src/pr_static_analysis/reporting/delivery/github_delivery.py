"""
GitHub delivery channel for PR static analysis reports.

This module provides the GitHubDelivery class for posting reports to GitHub.
"""

from typing import Dict, Any, Optional
import requests
from .base_delivery import BaseDelivery

class GitHubDelivery(BaseDelivery):
    """Delivery channel for GitHub comments."""
    
    def __init__(self, github_token: str = None, github_client = None):
        """
        Initialize the GitHub delivery channel.
        
        Args:
            github_token: GitHub API token
            github_client: GitHub client instance (alternative to token)
        """
        super().__init__()
        self.github_token = github_token
        self.github_client = github_client
        
    def deliver(self, report: str, **kwargs) -> bool:
        """
        Deliver a report as a GitHub comment.
        
        Args:
            report: Report content
            **kwargs: Additional arguments for the delivery
                repo_name: Repository name (e.g., "owner/repo")
                pr_number: Pull request number
                commit_sha: Commit SHA (for commit comments)
                is_review: Whether to post as a review comment
            
        Returns:
            True if delivery was successful, False otherwise
        """
        repo_name = kwargs.get("repo_name")
        pr_number = kwargs.get("pr_number")
        commit_sha = kwargs.get("commit_sha")
        is_review = kwargs.get("is_review", False)
        
        if not repo_name:
            self.logger.error("Repository name is required")
            return False
            
        # If using the GitHub client
        if self.github_client:
            try:
                if pr_number:
                    if is_review:
                        self.github_client.create_review(repo_name, pr_number, report)
                    else:
                        self.github_client.post_comment(repo_name, pr_number, report)
                elif commit_sha:
                    self.github_client.post_commit_comment(repo_name, commit_sha, report)
                else:
                    self.logger.error("Either PR number or commit SHA is required")
                    return False
                    
                self.logger.info(f"Report delivered to GitHub: {repo_name}")
                return True
            except Exception as e:
                self.logger.error(f"Error delivering report to GitHub: {e}")
                return False
        
        # If using the GitHub API directly
        elif self.github_token:
            try:
                headers = {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                if pr_number:
                    if is_review:
                        url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/reviews"
                        data = {"body": report, "event": "COMMENT"}
                    else:
                        url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
                        data = {"body": report}
                elif commit_sha:
                    url = f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}/comments"
                    data = {"body": report}
                else:
                    self.logger.error("Either PR number or commit SHA is required")
                    return False
                    
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                self.logger.info(f"Report delivered to GitHub: {repo_name}")
                return True
            except Exception as e:
                self.logger.error(f"Error delivering report to GitHub: {e}")
                return False
        else:
            self.logger.error("Either GitHub token or GitHub client is required")
            return False

