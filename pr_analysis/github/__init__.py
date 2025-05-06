"""
GitHub integration for the PR static analysis system.

This module contains classes for interacting with GitHub's API and webhooks.
"""

from .pr_client import PRClient
from .webhook_handler import WebhookHandler
from .comment_formatter import CommentFormatter

__all__ = ["PRClient", "WebhookHandler", "CommentFormatter"]

