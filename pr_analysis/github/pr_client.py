"""
GitHub PR client for interacting with GitHub's API.

This module provides a client for interacting with GitHub's API to fetch PR data.
"""

import logging
import requests
from typing import Dict, List, Optional, Any
import json

from ..utils.config_utils import Config

logger = logging.getLogger(__name__)


class PRClient:
    """
    Client for interacting with GitHub's API.
    
    This class provides methods for fetching PR data from GitHub.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize a new PR client.
        
        Args:
            config: Optional configuration
        """
        self.config = config or Config()
        self.github_token = self.config.get("github_token")
        self.github_api_url = self.config.get("github_api_url", "https://api.github.com")
        
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for GitHub API requests.
        
        Returns:
            A dictionary of headers
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        return headers
        
    def get_pr(self, repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """
        Get a PR from GitHub.
        
        Args:
            repo_owner: The owner of the repository
            repo_name: The name of the repository
            pr_number: The PR number
            
        Returns:
            A dictionary with PR data
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code != 200:
            logger.error(f"Failed to get PR {pr_number}: {response.status_code} {response.text}")
            return {}
            
        return response.json()
        
    def get_pr_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get the files changed in a PR.
        
        Args:
            repo_owner: The owner of the repository
            repo_name: The name of the repository
            pr_number: The PR number
            
        Returns:
            A list of dictionaries with file data
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code != 200:
            logger.error(f"Failed to get PR files: {response.status_code} {response.text}")
            return []
            
        return response.json()
        
    def get_pr_commits(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get the commits in a PR.
        
        Args:
            repo_owner: The owner of the repository
            repo_name: The name of the repository
            pr_number: The PR number
            
        Returns:
            A list of dictionaries with commit data
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code != 200:
            logger.error(f"Failed to get PR commits: {response.status_code} {response.text}")
            return []
            
        return response.json()
        
    def create_pr_comment(self, repo_owner: str, repo_name: str, pr_number: int, 
                         body: str) -> Dict[str, Any]:
        """
        Create a comment on a PR.
        
        Args:
            repo_owner: The owner of the repository
            repo_name: The name of the repository
            pr_number: The PR number
            body: The comment body
            
        Returns:
            A dictionary with the created comment data
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        data = {"body": body}
        response = requests.post(url, headers=self._get_headers(), json=data)
        
        if response.status_code != 201:
            logger.error(f"Failed to create PR comment: {response.status_code} {response.text}")
            return {}
            
        return response.json()
        
    def create_pr_review_comment(self, repo_owner: str, repo_name: str, pr_number: int,
                               body: str, commit_id: str, path: str, 
                               position: int) -> Dict[str, Any]:
        """
        Create a review comment on a PR.
        
        Args:
            repo_owner: The owner of the repository
            repo_name: The name of the repository
            pr_number: The PR number
            body: The comment body
            commit_id: The commit ID
            path: The file path
            position: The position in the diff
            
        Returns:
            A dictionary with the created comment data
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"
        data = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "position": position,
        }
        response = requests.post(url, headers=self._get_headers(), json=data)
        
        if response.status_code != 201:
            logger.error(f"Failed to create PR review comment: {response.status_code} {response.text}")
            return {}
            
        return response.json()
        
    def create_pr_review(self, repo_owner: str, repo_name: str, pr_number: int,
                        body: str, event: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a review on a PR.
        
        Args:
            repo_owner: The owner of the repository
            repo_name: The name of the repository
            pr_number: The PR number
            body: The review body
            event: The review event ("APPROVE", "REQUEST_CHANGES", "COMMENT")
            comments: A list of review comments
            
        Returns:
            A dictionary with the created review data
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
        data = {
            "body": body,
            "event": event,
            "comments": comments,
        }
        response = requests.post(url, headers=self._get_headers(), json=data)
        
        if response.status_code != 201:
            logger.error(f"Failed to create PR review: {response.status_code} {response.text}")
            return {}
            
        return response.json()
        
    def parse_repo_string(self, repo_string: str) -> tuple:
        """
        Parse a repository string into owner and name.
        
        Args:
            repo_string: The repository string (e.g., "owner/name")
            
        Returns:
            A tuple of (owner, name)
        """
        parts = repo_string.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository string: {repo_string}")
            
        return parts[0], parts[1]

