"""
Unit tests for the GitHubWebhookHandler class.
"""

import unittest
from unittest.mock import MagicMock, patch
import hmac
import hashlib
import json

from ida_pro_mcp.github_integration.webhook_handler import GitHubWebhookHandler


class TestGitHubWebhookHandler(unittest.TestCase):
    """
    Test cases for the GitHubWebhookHandler class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.pr_analyzer = MagicMock()
        self.pr_client = MagicMock()
        self.comment_formatter = MagicMock()
        self.webhook_secret = "test_secret"
        
        self.handler = GitHubWebhookHandler(
            pr_analyzer=self.pr_analyzer,
            pr_client=self.pr_client,
            comment_formatter=self.comment_formatter,
            webhook_secret=self.webhook_secret
        )
    
    def test_validate_signature_valid(self):
        """
        Test validating a valid signature.
        """
        payload = b'{"test": "data"}'
        
        # Compute the signature
        signature = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Validate the signature
        result = self.handler.validate_signature(payload, signature)
        self.assertTrue(result)
    
    def test_validate_signature_invalid(self):
        """
        Test validating an invalid signature.
        """
        payload = b'{"test": "data"}'
        signature = "sha256=invalid"
        
        # Validate the signature
        result = self.handler.validate_signature(payload, signature)
        self.assertFalse(result)
    
    def test_validate_signature_no_secret(self):
        """
        Test validating a signature when no secret is configured.
        """
        handler = GitHubWebhookHandler(
            pr_analyzer=self.pr_analyzer,
            pr_client=self.pr_client,
            comment_formatter=self.comment_formatter,
            webhook_secret=None
        )
        
        payload = b'{"test": "data"}'
        signature = "sha256=invalid"
        
        # Validate the signature
        result = handler.validate_signature(payload, signature)
        self.assertTrue(result)
    
    def test_handle_webhook_ping(self):
        """
        Test handling a ping event.
        """
        event_type = "ping"
        payload = {"zen": "Keep it simple"}
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Pong!")
    
    def test_handle_webhook_unsupported_event(self):
        """
        Test handling an unsupported event.
        """
        event_type = "unsupported"
        payload = {}
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "ignored")
        self.assertIn("Unsupported event type", result["message"])
    
    def test_handle_webhook_invalid_signature(self):
        """
        Test handling a webhook with an invalid signature.
        """
        event_type = "pull_request"
        payload = {"action": "opened"}
        signature = "sha256=invalid"
        raw_payload = b'{"action": "opened"}'
        
        with self.assertRaises(ValueError):
            self.handler.handle_webhook(event_type, payload, signature, raw_payload)
    
    def test_handle_pull_request_event_opened(self):
        """
        Test handling a pull_request opened event.
        """
        event_type = "pull_request"
        payload = {
            "action": "opened",
            "pull_request": {"number": 123},
            "repository": {"full_name": "test/repo"}
        }
        
        # Mock analyze_pr and post_results
        self.pr_analyzer.analyze_pr.return_value = {"issues": []}
        self.pr_client.get_pr.return_value = {"number": 123}
        self.comment_formatter.format_results.return_value = "No issues found"
        self.comment_formatter.format_summary.return_value = "✅ No issues found"
        self.pr_client.post_comment.return_value = True
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["pr_number"], 123)
        self.assertEqual(result["repo"], "test/repo")
        self.assertEqual(result["results_summary"], "✅ No issues found")
        
        # Verify method calls
        self.pr_client.get_pr.assert_called_once_with("test/repo", 123)
        self.pr_analyzer.analyze_pr.assert_called_once()
        self.comment_formatter.format_results.assert_called_once_with({"issues": []})
        self.pr_client.post_comment.assert_called_once_with("test/repo", 123, "No issues found")
    
    def test_handle_pull_request_event_synchronize(self):
        """
        Test handling a pull_request synchronize event.
        """
        event_type = "pull_request"
        payload = {
            "action": "synchronize",
            "pull_request": {"number": 123},
            "repository": {"full_name": "test/repo"}
        }
        
        # Mock analyze_pr and post_results
        self.pr_analyzer.analyze_pr.return_value = {"issues": []}
        self.pr_client.get_pr.return_value = {"number": 123}
        self.comment_formatter.format_results.return_value = "No issues found"
        self.comment_formatter.format_summary.return_value = "✅ No issues found"
        self.pr_client.post_comment.return_value = True
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["pr_number"], 123)
        self.assertEqual(result["repo"], "test/repo")
        
        # Verify method calls
        self.pr_client.get_pr.assert_called_once_with("test/repo", 123)
        self.pr_analyzer.analyze_pr.assert_called_once()
        self.comment_formatter.format_results.assert_called_once_with({"issues": []})
        self.pr_client.post_comment.assert_called_once_with("test/repo", 123, "No issues found")
    
    def test_handle_pull_request_event_reopened(self):
        """
        Test handling a pull_request reopened event.
        """
        event_type = "pull_request"
        payload = {
            "action": "reopened",
            "pull_request": {"number": 123},
            "repository": {"full_name": "test/repo"}
        }
        
        # Mock analyze_pr and post_results
        self.pr_analyzer.analyze_pr.return_value = {"issues": []}
        self.pr_client.get_pr.return_value = {"number": 123}
        self.comment_formatter.format_results.return_value = "No issues found"
        self.comment_formatter.format_summary.return_value = "✅ No issues found"
        self.pr_client.post_comment.return_value = True
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["pr_number"], 123)
        self.assertEqual(result["repo"], "test/repo")
        
        # Verify method calls
        self.pr_client.get_pr.assert_called_once_with("test/repo", 123)
        self.pr_analyzer.analyze_pr.assert_called_once()
        self.comment_formatter.format_results.assert_called_once_with({"issues": []})
        self.pr_client.post_comment.assert_called_once_with("test/repo", 123, "No issues found")
    
    def test_handle_pull_request_event_ignored_action(self):
        """
        Test handling a pull_request event with an ignored action.
        """
        event_type = "pull_request"
        payload = {
            "action": "closed",
            "pull_request": {"number": 123},
            "repository": {"full_name": "test/repo"}
        }
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "ignored")
        self.assertIn("Ignored pull_request event with action: closed", result["message"])
        self.assertEqual(result["pr_number"], 123)
        self.assertEqual(result["repo"], "test/repo")
        
        # Verify no analysis was performed
        self.pr_analyzer.analyze_pr.assert_not_called()
        self.pr_client.post_comment.assert_not_called()
    
    def test_handle_pull_request_event_error(self):
        """
        Test handling a pull_request event that raises an error.
        """
        event_type = "pull_request"
        payload = {
            "action": "opened",
            "pull_request": {"number": 123},
            "repository": {"full_name": "test/repo"}
        }
        
        # Mock analyze_pr to raise an exception
        self.pr_analyzer.analyze_pr.side_effect = Exception("Test error")
        
        result = self.handler.handle_webhook(event_type, payload)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Error analyzing PR", result["message"])
        self.assertEqual(result["pr_number"], 123)
        self.assertEqual(result["repo"], "test/repo")
    
    def test_analyze_pr(self):
        """
        Test analyzing a PR.
        """
        # Mock PR data and analysis results
        pr_data = {"number": 123}
        analysis_results = {"issues": []}
        
        self.pr_client.get_pr.return_value = pr_data
        self.pr_analyzer.analyze_pr.return_value = analysis_results
        
        # Call the method
        result = self.handler.analyze_pr("test/repo", 123)
        
        # Verify the result
        self.assertEqual(result, analysis_results)
        
        # Verify method calls
        self.pr_client.get_pr.assert_called_once_with("test/repo", 123)
        self.pr_analyzer.analyze_pr.assert_called_once_with("test/repo", 123, pr_data)
    
    def test_post_results(self):
        """
        Test posting analysis results.
        """
        # Mock formatting and posting
        results = {"issues": []}
        formatted_results = "No issues found"
        
        self.comment_formatter.format_results.return_value = formatted_results
        self.pr_client.post_comment.return_value = True
        
        # Call the method
        result = self.handler.post_results("test/repo", 123, results)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify method calls
        self.comment_formatter.format_results.assert_called_once_with(results)
        self.pr_client.post_comment.assert_called_once_with("test/repo", 123, formatted_results)


if __name__ == "__main__":
    unittest.main()

