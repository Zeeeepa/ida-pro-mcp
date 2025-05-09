"""
Unit tests for the GitHubPRClient class.
"""

import unittest
from unittest.mock import MagicMock, patch
from github.GithubException import GithubException

from ida_pro_mcp.github_integration.pr_client import GitHubPRClient


class TestGitHubPRClient(unittest.TestCase):
    """
    Test cases for the GitHubPRClient class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.token = "test_token"
        self.client = GitHubPRClient(self.token)
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_init(self, mock_github):
        """
        Test initialization of the client.
        """
        client = GitHubPRClient(self.token)
        mock_github.assert_called_once_with(self.token)
        self.assertEqual(client.token, self.token)
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_get_pr(self, mock_github):
        """
        Test getting PR data.
        """
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_file = MagicMock()
        mock_commit = MagicMock()
        
        # Set up mock return values
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_files.return_value = [mock_file]
        mock_pr.get_commits.return_value = [mock_commit]
        
        # Set up PR attributes
        mock_pr.number = 123
        mock_pr.title = "Test PR"
        mock_pr.body = "Test PR body"
        mock_pr.base.sha = "base_sha"
        mock_pr.head.sha = "head_sha"
        mock_pr.user.login = "test_user"
        mock_pr.created_at = "2023-01-01"
        mock_pr.updated_at = "2023-01-02"
        mock_pr.state = "open"
        
        # Call the method
        result = self.client.get_pr("test/repo", 123)
        
        # Verify the result
        self.assertEqual(result["number"], 123)
        self.assertEqual(result["title"], "Test PR")
        self.assertEqual(result["body"], "Test PR body")
        self.assertEqual(result["base_commit"], "base_sha")
        self.assertEqual(result["head_commit"], "head_sha")
        self.assertEqual(result["user"], "test_user")
        self.assertEqual(result["created_at"], "2023-01-01")
        self.assertEqual(result["updated_at"], "2023-01-02")
        self.assertEqual(result["state"], "open")
        self.assertEqual(len(result["changed_files"]), 1)
        self.assertEqual(len(result["commits"]), 1)
        
        # Verify the API calls
        mock_github.return_value.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_pr.get_files.assert_called_once()
        mock_pr.get_commits.assert_called_once()
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_get_pr_error(self, mock_github):
        """
        Test error handling when getting PR data.
        """
        # Mock GitHub API to raise an exception
        mock_github.return_value.get_repo.side_effect = GithubException(404, "Not found")
        
        # Call the method and verify it raises the exception
        with self.assertRaises(GithubException):
            self.client.get_pr("test/repo", 123)
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_post_comment(self, mock_github):
        """
        Test posting a comment on a PR.
        """
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        
        # Set up mock return values
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        
        # Call the method
        result = self.client.post_comment("test/repo", 123, "Test comment")
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the API calls
        mock_github.return_value.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_pr.create_issue_comment.assert_called_once_with("Test comment")
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_post_comment_error(self, mock_github):
        """
        Test error handling when posting a comment.
        """
        # Mock GitHub API to raise an exception
        mock_github.return_value.get_repo.side_effect = GithubException(404, "Not found")
        
        # Call the method and verify it raises the exception
        with self.assertRaises(GithubException):
            self.client.post_comment("test/repo", 123, "Test comment")
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_get_file_content(self, mock_github):
        """
        Test getting file content.
        """
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_content = MagicMock()
        
        # Set up mock return values
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_repo.get_contents.return_value = mock_content
        mock_content.decoded_content = b"Test content"
        mock_pr.head.sha = "head_sha"
        
        # Call the method
        result = self.client.get_file_content("test/repo", 123, "test.py")
        
        # Verify the result
        self.assertEqual(result, "Test content")
        
        # Verify the API calls
        mock_github.return_value.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_repo.get_contents.assert_called_once_with("test.py", ref="head_sha")
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_get_file_content_error(self, mock_github):
        """
        Test error handling when getting file content.
        """
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        
        # Set up mock return values
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.head.sha = "head_sha"
        
        # Mock get_contents to raise an exception
        mock_repo.get_contents.side_effect = GithubException(404, "Not found")
        
        # Call the method
        result = self.client.get_file_content("test/repo", 123, "test.py")
        
        # Verify the result
        self.assertIsNone(result)
        
        # Verify the API calls
        mock_github.return_value.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_repo.get_contents.assert_called_once_with("test.py", ref="head_sha")
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_get_diff(self, mock_github):
        """
        Test getting PR diff.
        """
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        
        # Set up mock return values
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.diff.return_value = "Test diff"
        
        # Call the method
        result = self.client.get_diff("test/repo", 123)
        
        # Verify the result
        self.assertEqual(result, "Test diff")
        
        # Verify the API calls
        mock_github.return_value.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_pr.diff.assert_called_once()
    
    @patch("ida_pro_mcp.github_integration.pr_client.Github")
    def test_get_diff_error(self, mock_github):
        """
        Test error handling when getting PR diff.
        """
        # Mock GitHub API to raise an exception
        mock_github.return_value.get_repo.side_effect = GithubException(404, "Not found")
        
        # Call the method and verify it raises the exception
        with self.assertRaises(GithubException):
            self.client.get_diff("test/repo", 123)


if __name__ == "__main__":
    unittest.main()

