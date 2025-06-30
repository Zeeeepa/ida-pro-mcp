"""
GitHub Webhook Server for handling GitHub webhook events.

This module provides a simple web server for receiving and processing
GitHub webhook events.
"""

import logging
import json
import os
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify

from .webhook_handler import GitHubWebhookHandler

logger = logging.getLogger(__name__)

class GitHubWebhookServer:
    """
    Server for handling GitHub webhook events.
    
    This class provides a Flask web server for receiving and processing
    GitHub webhook events.
    """
    
    def __init__(self, webhook_handler: GitHubWebhookHandler, 
                 host: str = "0.0.0.0", port: int = 5000):
        """
        Initialize the webhook server.
        
        Args:
            webhook_handler: Handler for processing webhook events
            host: Host to bind the server to
            port: Port to bind the server to
        """
        self.webhook_handler = webhook_handler
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self) -> None:
        """
        Register routes for the Flask app.
        """
        @self.app.route("/webhook", methods=["POST"])
        def webhook():
            # Get event type from header
            event_type = request.headers.get("X-GitHub-Event")
            if not event_type:
                return jsonify({"status": "error", "message": "Missing X-GitHub-Event header"}), 400
            
            # Get signature from header
            signature = request.headers.get("X-Hub-Signature-256")
            
            # Get payload
            if request.is_json:
                payload = request.json
                raw_payload = request.data
            else:
                try:
                    payload = json.loads(request.data)
                    raw_payload = request.data
                except json.JSONDecodeError:
                    return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400
            
            try:
                # Handle the webhook
                result = self.webhook_handler.handle_webhook(
                    event_type=event_type,
                    payload=payload,
                    signature=signature,
                    raw_payload=raw_payload
                )
                
                return jsonify(result)
            except ValueError as e:
                return jsonify({"status": "error", "message": str(e)}), 400
            except Exception as e:
                logger.exception(f"Error handling webhook: {e}")
                return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500
        
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "ok"})
    
    def run(self, debug: bool = False) -> None:
        """
        Run the webhook server.
        
        Args:
            debug: Whether to run the server in debug mode
        """
        self.app.run(host=self.host, port=self.port, debug=debug)


def create_webhook_server(webhook_handler: GitHubWebhookHandler, 
                         host: Optional[str] = None, 
                         port: Optional[int] = None) -> GitHubWebhookServer:
    """
    Create a webhook server.
    
    Args:
        webhook_handler: Handler for processing webhook events
        host: Host to bind the server to (defaults to WEBHOOK_HOST env var or "0.0.0.0")
        port: Port to bind the server to (defaults to WEBHOOK_PORT env var or 5000)
        
    Returns:
        Webhook server instance
    """
    # Get host and port from environment variables if not provided
    if host is None:
        host = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
    
    if port is None:
        port_str = os.environ.get("WEBHOOK_PORT", "5000")
        try:
            port = int(port_str)
        except ValueError:
            logger.warning(f"Invalid port: {port_str}, using default port 5000")
            port = 5000
    
    return GitHubWebhookServer(webhook_handler, host, port)


def main() -> None:
    """
    Run the webhook server as a standalone application.
    """
    import argparse
    from .pr_client import GitHubPRClient
    from .comment_formatter import GitHubCommentFormatter
    from .pr_analyzer import CorePRAnalyzer
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GitHub Webhook Server")
    parser.add_argument("--host", default=os.environ.get("WEBHOOK_HOST", "0.0.0.0"),
                        help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=int(os.environ.get("WEBHOOK_PORT", "5000")),
                        help="Port to bind the server to")
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"),
                        help="GitHub API token")
    parser.add_argument("--webhook-secret", default=os.environ.get("WEBHOOK_SECRET"),
                        help="Secret for validating webhook payloads")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Check if GitHub token is provided
    if not args.github_token:
        logger.error("GitHub token is required")
        parser.print_help()
        return
    
    # Create components
    pr_client = GitHubPRClient(args.github_token)
    comment_formatter = GitHubCommentFormatter()
    pr_analyzer = CorePRAnalyzer(pr_client)
    
    # Create webhook handler
    webhook_handler = GitHubWebhookHandler(
        pr_analyzer=pr_analyzer,
        pr_client=pr_client,
        comment_formatter=comment_formatter,
        webhook_secret=args.webhook_secret
    )
    
    # Create and run webhook server
    server = create_webhook_server(webhook_handler, args.host, args.port)
    logger.info(f"Starting webhook server on {args.host}:{args.port}")
    server.run(debug=args.debug)


if __name__ == "__main__":
    main()

