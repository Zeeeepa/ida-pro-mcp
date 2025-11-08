"""
GitHub Delivery Module

This module provides a delivery channel for sending reports to GitHub.
"""

import logging
from typing import Any, Dict, Optional, Union

from .base_delivery import BaseDelivery

try:
    from github import Github
    from github.Repository import Repository
    from github.PullRequest import PullRequest
    from github.Issue import Issue
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


class GitHubDelivery(BaseDelivery):
    """
    Delivery channel for sending reports to GitHub.
    
    This delivery channel can post reports as comments on GitHub issues or pull requests,
    or create new issues with the report content.
    """
    
    def __init__(
        self,
        token: str,
        repo_name: str,
        create_issue_if_not_exists: bool = False,
        issue_title_template: str = "PR Static Analysis Report: {pr_number}",
        issue_labels: Optional[list] = None
    ):
        """
        Initialize a new GitHubDelivery channel.
        
        Args:
            token: GitHub API token
            repo_name: Repository name in the format "owner/repo"
            create_issue_if_not_exists: Whether to create a new issue if the specified issue/PR doesn't exist
            issue_title_template: Template for the issue title when creating a new issue
            issue_labels: Labels to apply to new issues
        
        Raises:
            ImportError: If the github package is not installed
        """
        if not GITHUB_AVAILABLE:
            raise ImportError(
                "The github package is required for GitHubDelivery. "
                "Install it with: pip install PyGithub"
            )
        
        self.token = token
        self.repo_name = repo_name
        self.create_issue_if_not_exists = create_issue_if_not_exists
        self.issue_title_template = issue_title_template
        self.issue_labels = issue_labels or []
        
        # Initialize GitHub client
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)
        
    def deliver(
        self, 
        report: str, 
        **kwargs
    ) -> bool:
        """
        Deliver a report to GitHub.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments, including:
                - pr_number: Pull request number
                - issue_number: Issue number
                - comment_id: Comment ID to update (if updating an existing comment)
                - create_issue: Whether to create a new issue with the report
                - issue_title: Title for the new issue (if creating one)
                - issue_labels: Labels for the new issue (if creating one)
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            # Determine the target (PR, issue, or new issue)
            pr_number = kwargs.get('pr_number')
            issue_number = kwargs.get('issue_number')
            comment_id = kwargs.get('comment_id')
            create_issue = kwargs.get('create_issue', False)
            
            if pr_number:
                # Post to a pull request
                return self._deliver_to_pr(report, pr_number, comment_id)
            elif issue_number:
                # Post to an issue
                return self._deliver_to_issue(report, issue_number, comment_id)
            elif create_issue or self.create_issue_if_not_exists:
                # Create a new issue
                issue_title = kwargs.get('issue_title')
                if not issue_title and pr_number:
                    issue_title = self.issue_title_template.format(pr_number=pr_number)
                else:
                    issue_title = kwargs.get('issue_title', "PR Static Analysis Report")
                
                issue_labels = kwargs.get('issue_labels', self.issue_labels)
                
                return self._create_issue(report, issue_title, issue_labels)
            else:
                logging.error("No target specified for GitHub delivery")
                return False
        
        except Exception as e:
            logging.error(f"Error delivering report to GitHub: {e}")
            return False
    
    def _deliver_to_pr(self, report: str, pr_number: int, comment_id: Optional[int] = None) -> bool:
        """
        Deliver a report to a pull request.
        
        Args:
            report: The report to deliver
            pr_number: Pull request number
            comment_id: Comment ID to update (if updating an existing comment)
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            pr = self.repo.get_pull(pr_number)
            
            if comment_id:
                # Update an existing comment
                comment = self.repo.get_issue(pr_number).get_comment(comment_id)
                comment.edit(report)
            else:
                # Create a new comment
                pr.create_issue_comment(report)
            
            return True
        
        except Exception as e:
            logging.error(f"Error delivering report to PR #{pr_number}: {e}")
            
            if self.create_issue_if_not_exists:
                # Create a new issue instead
                issue_title = self.issue_title_template.format(pr_number=pr_number)
                return self._create_issue(report, issue_title, self.issue_labels)
            
            return False
    
    def _deliver_to_issue(self, report: str, issue_number: int, comment_id: Optional[int] = None) -> bool:
        """
        Deliver a report to an issue.
        
        Args:
            report: The report to deliver
            issue_number: Issue number
            comment_id: Comment ID to update (if updating an existing comment)
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            issue = self.repo.get_issue(issue_number)
            
            if comment_id:
                # Update an existing comment
                comment = issue.get_comment(comment_id)
                comment.edit(report)
            else:
                # Create a new comment
                issue.create_comment(report)
            
            return True
        
        except Exception as e:
            logging.error(f"Error delivering report to issue #{issue_number}: {e}")
            
            if self.create_issue_if_not_exists:
                # Create a new issue instead
                issue_title = f"PR Static Analysis Report (related to #{issue_number})"
                return self._create_issue(report, issue_title, self.issue_labels)
            
            return False
    
    def _create_issue(self, report: str, title: str, labels: Optional[list] = None) -> bool:
        """
        Create a new issue with the report.
        
        Args:
            report: The report to include in the issue body
            title: Issue title
            labels: Labels to apply to the issue
            
        Returns:
            True if issue creation was successful, False otherwise
        """
        try:
            self.repo.create_issue(title=title, body=report, labels=labels or [])
            return True
        
        except Exception as e:
            logging.error(f"Error creating issue: {e}")
            return False

