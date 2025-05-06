"""
GitHub Webhook Handler for processing GitHub webhook events.

This module provides a handler for GitHub webhook events, particularly
for pull request events that trigger static analysis.
"""

import hmac
import hashlib
import logging
import json
from typing import Dict, Any, Optional, Callable, Union

from .pr_client import GitHubPRClient
from .comment_formatter import GitHubCommentFormatter

logger = logging.getLogger(__name__)

class GitHubWebhookHandler:
    """
    Handler for GitHub webhook events.
    
    This class processes GitHub webhook events, validates payloads,
    and triggers analysis for pull request events.
    """
    
    def __init__(self, pr_analyzer: Any, pr_client: GitHubPRClient, 
                 comment_formatter: GitHubCommentFormatter, 
                 webhook_secret: Optional[str] = None):
        """
        Initialize the webhook handler.
        
        Args:
            pr_analyzer: PR analyzer instance that performs the static analysis
            pr_client: GitHub PR client for interacting with PRs
            comment_formatter: Formatter for analysis results
            webhook_secret: Secret for validating webhook payloads (optional)
        """
        self.pr_analyzer = pr_analyzer
        self.pr_client = pr_client
        self.comment_formatter = comment_formatter
        self.webhook_secret = webhook_secret
    
    def validate_signature(self, payload: bytes, signature: str) -> bool:
        """
        Validate the webhook signature.
        
        Args:
            payload: Raw webhook payload as bytes
            signature: Signature from the X-Hub-Signature-256 header
            
        Returns:
            True if the signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping signature validation")
            return True
        
        # Compute the HMAC
        computed_signature = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(computed_signature, signature)
    
    def handle_webhook(self, event_type: str, payload: Dict[str, Any], 
                       signature: Optional[str] = None, raw_payload: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Handle a GitHub webhook event.
        
        Args:
            event_type: Event type from the X-GitHub-Event header
            payload: Webhook payload as a dictionary
            signature: Signature from the X-Hub-Signature-256 header (optional)
            raw_payload: Raw webhook payload as bytes (required if signature is provided)
            
        Returns:
            Dictionary containing the result of handling the webhook
            
        Raises:
            ValueError: If signature validation fails
        """
        # Validate signature if provided
        if signature and raw_payload:
            if not self.validate_signature(raw_payload, signature):
                logger.error("Invalid webhook signature")
                raise ValueError("Invalid webhook signature")
        
        # Log the event
        logger.info(f"Received GitHub webhook event: {event_type}")
        
        # Handle different event types
        if event_type == "ping":
            logger.info("Received ping event")
            return {"status": "success", "message": "Pong!"}
        
        elif event_type == "pull_request":
            return self._handle_pull_request_event(payload)
        
        else:
            logger.info(f"Ignoring unsupported event type: {event_type}")
            return {"status": "ignored", "message": f"Unsupported event type: {event_type}"}
    
    def _handle_pull_request_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a pull request event.
        
        Args:
            payload: Webhook payload as a dictionary
            
        Returns:
            Dictionary containing the result of handling the event
        """
        action = payload.get("action")
        pr_number = payload["pull_request"]["number"]
        repo = payload["repository"]["full_name"]
        
        logger.info(f"Received pull_request event: {action} for PR #{pr_number} in {repo}")
        
        # Only analyze PRs that are opened, synchronized, or reopened
        if action in ["opened", "synchronize", "reopened"]:
            try:
                # Analyze the PR
                results = self.analyze_pr(repo, pr_number)
                
                # Post results as a comment
                self.post_results(repo, pr_number, results)
                
                return {
                    "status": "success",
                    "message": f"Analyzed PR #{pr_number} in {repo}",
                    "pr_number": pr_number,
                    "repo": repo,
                    "results_summary": self.comment_formatter.format_summary(results)
                }
            except Exception as e:
                logger.error(f"Error analyzing PR #{pr_number} in {repo}: {e}")
                return {
                    "status": "error",
                    "message": f"Error analyzing PR: {str(e)}",
                    "pr_number": pr_number,
                    "repo": repo
                }
        else:
            logger.info(f"Ignoring pull_request event with action: {action}")
            return {
                "status": "ignored",
                "message": f"Ignored pull_request event with action: {action}",
                "pr_number": pr_number,
                "repo": repo
            }
    
    def analyze_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Analyze a pull request.
        
        Args:
            repo: Repository name in the format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing PR #{pr_number} in {repo}")
        
        # Get PR data
        pr_data = self.pr_client.get_pr(repo, pr_number)
        
        # Analyze the PR
        results = self.pr_analyzer.analyze_pr(repo, pr_number, pr_data)
        
        return results
    
    def post_results(self, repo: str, pr_number: int, results: Dict[str, Any]) -> bool:
        """
        Post analysis results as a comment on the PR.
        
        Args:
            repo: Repository name in the format "owner/repo"
            pr_number: Pull request number
            results: Analysis results
            
        Returns:
            True if the results were posted successfully, False otherwise
        """
        logger.info(f"Posting analysis results for PR #{pr_number} in {repo}")
        
        # Format the results as a comment
        comment = self.comment_formatter.format_results(results)
        
        # Post the comment
        return self.pr_client.post_comment(repo, pr_number, comment)

