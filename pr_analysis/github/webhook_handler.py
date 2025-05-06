"""
Webhook handler for GitHub webhooks.

This module provides a handler for GitHub webhooks.
"""

import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Callable

from ..core.pr_analyzer import PRAnalyzer
from ..utils.config_utils import Config

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Handler for GitHub webhooks.
    
    This class provides methods for handling GitHub webhook events.
    """
    
    def __init__(self, config: Optional[Config] = None, analyzer: Optional[PRAnalyzer] = None):
        """
        Initialize a new webhook handler.
        
        Args:
            config: Optional configuration
            analyzer: Optional PR analyzer
        """
        self.config = config or Config()
        self.analyzer = analyzer or PRAnalyzer()
        self.webhook_secret = self.config.get("github_webhook_secret")
        self.event_handlers: Dict[str, Callable] = {
            "pull_request": self.handle_pull_request,
            "pull_request_review": self.handle_pull_request_review,
            "push": self.handle_push,
        }
        
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify the webhook signature.
        
        Args:
            payload: The webhook payload
            signature: The webhook signature
            
        Returns:
            True if the signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping signature verification")
            return True
            
        if not signature:
            logger.warning("No signature provided")
            return False
            
        # Extract algorithm and signature
        parts = signature.split("=", 1)
        if len(parts) != 2:
            logger.warning(f"Invalid signature format: {signature}")
            return False
            
        algorithm, signature = parts
        
        # Verify signature
        if algorithm == "sha1":
            mac = hmac.new(self.webhook_secret.encode(), payload, hashlib.sha1)
        elif algorithm == "sha256":
            mac = hmac.new(self.webhook_secret.encode(), payload, hashlib.sha256)
        else:
            logger.warning(f"Unsupported signature algorithm: {algorithm}")
            return False
            
        expected_signature = mac.hexdigest()
        return hmac.compare_digest(signature, expected_signature)
        
    def handle_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a webhook event.
        
        Args:
            event_type: The event type
            payload: The webhook payload
            
        Returns:
            A dictionary with the result of handling the webhook
        """
        handler = self.event_handlers.get(event_type)
        if not handler:
            logger.info(f"No handler for event type: {event_type}")
            return {"status": "ignored", "reason": f"No handler for event type: {event_type}"}
            
        try:
            return handler(payload)
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"status": "error", "reason": str(e)}
            
    def handle_pull_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a pull_request event.
        
        Args:
            payload: The webhook payload
            
        Returns:
            A dictionary with the result of handling the webhook
        """
        action = payload.get("action")
        if action not in ["opened", "synchronize", "reopened"]:
            logger.info(f"Ignoring pull_request action: {action}")
            return {"status": "ignored", "reason": f"Ignoring pull_request action: {action}"}
            
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        
        pr_id = pr.get("number")
        repo_name = repo.get("full_name")
        base_branch = pr.get("base", {}).get("ref")
        head_branch = pr.get("head", {}).get("ref")
        
        if not all([pr_id, repo_name, base_branch, head_branch]):
            logger.warning("Missing required PR information")
            return {"status": "error", "reason": "Missing required PR information"}
            
        # Get PR files
        from .pr_client import PRClient
        client = PRClient(self.config)
        repo_owner, repo_name = client.parse_repo_string(repo_name)
        files = client.get_pr_files(repo_owner, repo_name, pr_id)
        
        # Convert files to the format expected by the analyzer
        file_changes = []
        for file in files:
            file_changes.append({
                "filename": file.get("filename"),
                "status": file.get("status"),
                "patch": file.get("patch"),
            })
            
        # Analyze PR
        context, report = self.analyzer.analyze_pr(
            pr_id=str(pr_id),
            repo_name=repo_name,
            base_branch=base_branch,
            head_branch=head_branch,
            file_changes=file_changes,
        )
        
        # Post results as a comment
        from .comment_formatter import CommentFormatter
        formatter = CommentFormatter()
        comment = formatter.format_results(context.results)
        
        if comment:
            client.create_pr_comment(repo_owner, repo_name, pr_id, comment)
            
        return {
            "status": "success",
            "pr_id": pr_id,
            "repo_name": repo_name,
            "results_count": len(context.results),
        }
        
    def handle_pull_request_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a pull_request_review event.
        
        Args:
            payload: The webhook payload
            
        Returns:
            A dictionary with the result of handling the webhook
        """
        # Placeholder for pull_request_review handling
        return {"status": "ignored", "reason": "pull_request_review handling not implemented"}
        
    def handle_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a push event.
        
        Args:
            payload: The webhook payload
            
        Returns:
            A dictionary with the result of handling the webhook
        """
        # Placeholder for push handling
        return {"status": "ignored", "reason": "push handling not implemented"}

