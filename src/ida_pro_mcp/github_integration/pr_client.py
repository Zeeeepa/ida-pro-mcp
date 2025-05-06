"""
GitHub PR Client for interacting with GitHub pull requests.

This module provides a client for retrieving PR data from GitHub and
posting comments on PRs.
"""

import logging
from typing import Dict, List, Any, Optional
from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.GithubException import GithubException

logger = logging.getLogger(__name__)

class GitHubPRClient:
    """
    Client for interacting with GitHub pull requests.
    
    This class provides methods for retrieving PR data and posting comments
    on PRs using the GitHub API.
    """
    
    def __init__(self, token: str):
        """
        Initialize the GitHub PR client.
        
        Args:
            token: GitHub API token for authentication
        """
        self.token = token
        self.github = Github(token)
    
    def get_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request data from GitHub.
        
        Args:
            repo: Repository name in the format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            Dictionary containing PR data including files, commits, and metadata
            
        Raises:
            GithubException: If the PR cannot be retrieved
        """
        try:
            # Get repository
            repo_obj = self.github.get_repo(repo)
            
            # Get pull request
            pr = repo_obj.get_pull(pr_number)
            
            # Get PR data
            pr_data = {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "base_commit": pr.base.sha,
                "head_commit": pr.head.sha,
                "changed_files": list(pr.get_files()),
                "commits": list(pr.get_commits()),
                "user": pr.user.login,
                "created_at": pr.created_at,
                "updated_at": pr.updated_at,
                "state": pr.state,
            }
            
            return pr_data
        except GithubException as e:
            logger.error(f"Error retrieving PR {pr_number} from {repo}: {e}")
            raise
    
    def post_comment(self, repo: str, pr_number: int, comment: str) -> bool:
        """
        Post a comment on a pull request.
        
        Args:
            repo: Repository name in the format "owner/repo"
            pr_number: Pull request number
            comment: Comment text to post
            
        Returns:
            True if the comment was posted successfully, False otherwise
            
        Raises:
            GithubException: If the comment cannot be posted
        """
        try:
            # Get repository
            repo_obj = self.github.get_repo(repo)
            
            # Get pull request
            pr = repo_obj.get_pull(pr_number)
            
            # Create comment
            pr.create_issue_comment(comment)
            logger.info(f"Posted comment on PR {pr_number} in {repo}")
            return True
        except GithubException as e:
            logger.error(f"Error posting comment on PR {pr_number} in {repo}: {e}")
            raise
    
    def get_file_content(self, repo: str, pr_number: int, file_path: str) -> Optional[str]:
        """
        Get the content of a file in a pull request.
        
        Args:
            repo: Repository name in the format "owner/repo"
            pr_number: Pull request number
            file_path: Path to the file
            
        Returns:
            Content of the file as a string, or None if the file cannot be retrieved
        """
        try:
            # Get repository
            repo_obj = self.github.get_repo(repo)
            
            # Get pull request
            pr = repo_obj.get_pull(pr_number)
            
            # Get file content from the head commit
            content = repo_obj.get_contents(file_path, ref=pr.head.sha)
            return content.decoded_content.decode('utf-8')
        except GithubException as e:
            logger.error(f"Error retrieving file {file_path} from PR {pr_number} in {repo}: {e}")
            return None
    
    def get_diff(self, repo: str, pr_number: int) -> str:
        """
        Get the diff for a pull request.
        
        Args:
            repo: Repository name in the format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            Diff as a string
        """
        try:
            # Get repository
            repo_obj = self.github.get_repo(repo)
            
            # Get pull request
            pr = repo_obj.get_pull(pr_number)
            
            # Get diff
            return pr.diff()
        except GithubException as e:
            logger.error(f"Error retrieving diff for PR {pr_number} in {repo}: {e}")
            raise

