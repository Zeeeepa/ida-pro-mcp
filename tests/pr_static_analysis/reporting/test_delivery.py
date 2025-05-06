"""
Tests for the delivery channels.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
import requests
import smtplib
from src.pr_static_analysis.reporting.delivery.file_delivery import FileDelivery
from src.pr_static_analysis.reporting.delivery.github_delivery import GitHubDelivery
from src.pr_static_analysis.reporting.delivery.slack_delivery import SlackDelivery
from src.pr_static_analysis.reporting.delivery.email_delivery import EmailDelivery

class TestFileDelivery(unittest.TestCase):
    """Tests for the FileDelivery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_delivery = FileDelivery()
        self.report = "Test report content"
        
    @patch("builtins.open", new_callable=mock_open)
    def test_deliver(self, mock_file):
        """Test delivering a report to a file."""
        result = self.file_delivery.deliver(self.report, file_path="test.txt")
        
        # Check that the file was opened and written to
        mock_file.assert_called_once_with("test.txt", "w")
        mock_file().write.assert_called_once_with(self.report)
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_no_file_path(self):
        """Test delivering a report without a file path."""
        result = self.file_delivery.deliver(self.report)
        
        # Check the result
        self.assertFalse(result)
        
    @patch("builtins.open", side_effect=IOError("Test error"))
    def test_deliver_error(self, mock_file):
        """Test delivering a report with an error."""
        result = self.file_delivery.deliver(self.report, file_path="test.txt")
        
        # Check the result
        self.assertFalse(result)

class TestGitHubDelivery(unittest.TestCase):
    """Tests for the GitHubDelivery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_client = MagicMock()
        self.github_delivery = GitHubDelivery(github_client=self.github_client)
        self.report = "Test report content"
        
    def test_deliver_pr_comment(self):
        """Test delivering a report as a PR comment."""
        result = self.github_delivery.deliver(
            self.report, repo_name="test/repo", pr_number=123
        )
        
        # Check that the client was called
        self.github_client.post_comment.assert_called_once_with(
            "test/repo", 123, self.report
        )
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_pr_review(self):
        """Test delivering a report as a PR review."""
        result = self.github_delivery.deliver(
            self.report, repo_name="test/repo", pr_number=123, is_review=True
        )
        
        # Check that the client was called
        self.github_client.create_review.assert_called_once_with(
            "test/repo", 123, self.report
        )
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_commit_comment(self):
        """Test delivering a report as a commit comment."""
        result = self.github_delivery.deliver(
            self.report, repo_name="test/repo", commit_sha="abc123"
        )
        
        # Check that the client was called
        self.github_client.post_commit_comment.assert_called_once_with(
            "test/repo", "abc123", self.report
        )
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_no_repo_name(self):
        """Test delivering a report without a repository name."""
        result = self.github_delivery.deliver(self.report, pr_number=123)
        
        # Check the result
        self.assertFalse(result)
        
    def test_deliver_no_pr_or_commit(self):
        """Test delivering a report without a PR number or commit SHA."""
        result = self.github_delivery.deliver(self.report, repo_name="test/repo")
        
        # Check the result
        self.assertFalse(result)
        
    def test_deliver_client_error(self):
        """Test delivering a report with a client error."""
        self.github_client.post_comment.side_effect = Exception("Test error")
        
        result = self.github_delivery.deliver(
            self.report, repo_name="test/repo", pr_number=123
        )
        
        # Check the result
        self.assertFalse(result)
        
    @patch("requests.post")
    def test_deliver_with_token(self, mock_post):
        """Test delivering a report with a token."""
        # Create a delivery with a token
        github_delivery = GitHubDelivery(github_token="test_token")
        
        # Mock the response
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        result = github_delivery.deliver(
            self.report, repo_name="test/repo", pr_number=123
        )
        
        # Check that the request was made
        mock_post.assert_called_once()
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_no_client_or_token(self):
        """Test delivering a report without a client or token."""
        github_delivery = GitHubDelivery()
        
        result = github_delivery.deliver(
            self.report, repo_name="test/repo", pr_number=123
        )
        
        # Check the result
        self.assertFalse(result)

class TestSlackDelivery(unittest.TestCase):
    """Tests for the SlackDelivery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.slack_client = MagicMock()
        self.slack_delivery = SlackDelivery(slack_client=self.slack_client)
        self.report = "Test report content"
        
    def test_deliver_with_client(self):
        """Test delivering a report with a client."""
        result = self.slack_delivery.deliver(
            self.report, channel="#test", username="Test Bot", icon_emoji=":test:"
        )
        
        # Check that the client was called
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel="#test", text=self.report, username="Test Bot", icon_emoji=":test:"
        )
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_with_blocks(self):
        """Test delivering a report with blocks."""
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": self.report}}]
        
        result = self.slack_delivery.deliver(
            self.report, channel="#test", blocks=blocks
        )
        
        # Check that the client was called
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel="#test", blocks=blocks
        )
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_client_error(self):
        """Test delivering a report with a client error."""
        self.slack_client.chat_postMessage.side_effect = Exception("Test error")
        
        result = self.slack_delivery.deliver(self.report, channel="#test")
        
        # Check the result
        self.assertFalse(result)
        
    @patch("requests.post")
    def test_deliver_with_webhook(self, mock_post):
        """Test delivering a report with a webhook."""
        # Create a delivery with a webhook
        slack_delivery = SlackDelivery(webhook_url="https://hooks.slack.com/test")
        
        # Mock the response
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        result = slack_delivery.deliver(
            self.report, channel="#test", username="Test Bot", icon_emoji=":test:"
        )
        
        # Check that the request was made
        mock_post.assert_called_once()
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_no_client_or_webhook(self):
        """Test delivering a report without a client or webhook."""
        slack_delivery = SlackDelivery()
        
        result = slack_delivery.deliver(self.report, channel="#test")
        
        # Check the result
        self.assertFalse(result)

class TestEmailDelivery(unittest.TestCase):
    """Tests for the EmailDelivery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.email_delivery = EmailDelivery(
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="test@example.com",
            password="password"
        )
        self.report = "Test report content"
        
    @patch("smtplib.SMTP")
    def test_deliver(self, mock_smtp):
        """Test delivering a report via email."""
        # Mock the SMTP instance
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        result = self.email_delivery.deliver(
            self.report,
            from_addr="from@example.com",
            to_addr="to@example.com",
            subject="Test Subject",
            is_html=False
        )
        
        # Check that the SMTP server was used
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("test@example.com", "password")
        mock_smtp_instance.sendmail.assert_called_once()
        
        # Check the result
        self.assertTrue(result)
        
    def test_deliver_no_from_addr(self):
        """Test delivering a report without a from address."""
        result = self.email_delivery.deliver(
            self.report, to_addr="to@example.com"
        )
        
        # Check the result
        self.assertFalse(result)
        
    def test_deliver_no_to_addr(self):
        """Test delivering a report without a to address."""
        result = self.email_delivery.deliver(
            self.report, from_addr="from@example.com"
        )
        
        # Check the result
        self.assertFalse(result)
        
    def test_deliver_no_smtp_server(self):
        """Test delivering a report without an SMTP server."""
        email_delivery = EmailDelivery(smtp_port=587)
        
        result = email_delivery.deliver(
            self.report,
            from_addr="from@example.com",
            to_addr="to@example.com"
        )
        
        # Check the result
        self.assertFalse(result)
        
    def test_deliver_no_smtp_port(self):
        """Test delivering a report without an SMTP port."""
        email_delivery = EmailDelivery(smtp_server="smtp.example.com")
        
        result = email_delivery.deliver(
            self.report,
            from_addr="from@example.com",
            to_addr="to@example.com"
        )
        
        # Check the result
        self.assertFalse(result)
        
    @patch("smtplib.SMTP", side_effect=smtplib.SMTPException("Test error"))
    def test_deliver_smtp_error(self, mock_smtp):
        """Test delivering a report with an SMTP error."""
        result = self.email_delivery.deliver(
            self.report,
            from_addr="from@example.com",
            to_addr="to@example.com"
        )
        
        # Check the result
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()

