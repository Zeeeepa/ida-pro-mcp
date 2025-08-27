"""
GitHub PR Analysis command-line script.

This module provides a command-line script for running the GitHub PR
analysis server and performing manual analysis of PRs.
"""

import logging
import os
import sys
import argparse
from typing import Dict, Any, Optional

from .github_integration import (
    GitHubPRClient,
    GitHubCommentFormatter,
    CorePRAnalyzer,
    GitHubWebhookHandler,
    create_webhook_server
)

logger = logging.getLogger(__name__)

def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def analyze_pr(github_token: str, repo: str, pr_number: int, post_comment: bool = False) -> Dict[str, Any]:
    """
    Analyze a pull request.
    
    Args:
        github_token: GitHub API token
        repo: Repository name in the format "owner/repo"
        pr_number: Pull request number
        post_comment: Whether to post the analysis results as a comment
        
    Returns:
        Dictionary containing analysis results
    """
    # Create components
    pr_client = GitHubPRClient(github_token)
    comment_formatter = GitHubCommentFormatter()
    pr_analyzer = CorePRAnalyzer(pr_client)
    
    # Analyze the PR
    results = pr_analyzer.analyze_pr(repo, pr_number)
    
    # Post results as a comment if requested
    if post_comment:
        comment = comment_formatter.format_results(results)
        pr_client.post_comment(repo, pr_number, comment)
    
    return results

def run_webhook_server(github_token: str, webhook_secret: Optional[str] = None,
                      host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Run the webhook server.
    
    Args:
        github_token: GitHub API token
        webhook_secret: Secret for validating webhook payloads
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run the server in debug mode
    """
    # Create components
    pr_client = GitHubPRClient(github_token)
    comment_formatter = GitHubCommentFormatter()
    pr_analyzer = CorePRAnalyzer(pr_client)
    
    # Create webhook handler
    webhook_handler = GitHubWebhookHandler(
        pr_analyzer=pr_analyzer,
        pr_client=pr_client,
        comment_formatter=comment_formatter,
        webhook_secret=webhook_secret
    )
    
    # Create and run webhook server
    server = create_webhook_server(webhook_handler, host, port)
    logger.info(f"Starting webhook server on {host}:{port}")
    server.run(debug=debug)

def main() -> None:
    """
    Main entry point for the command-line script.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="GitHub PR Analysis")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Analyze PR command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a pull request")
    analyze_parser.add_argument("repo", help="Repository name in the format 'owner/repo'")
    analyze_parser.add_argument("pr_number", type=int, help="Pull request number")
    analyze_parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"),
                              help="GitHub API token")
    analyze_parser.add_argument("--post-comment", action="store_true",
                              help="Post analysis results as a comment")
    analyze_parser.add_argument("--verbose", "-v", action="store_true",
                              help="Enable verbose logging")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the webhook server")
    server_parser.add_argument("--host", default=os.environ.get("WEBHOOK_HOST", "0.0.0.0"),
                             help="Host to bind the server to")
    server_parser.add_argument("--port", type=int, default=int(os.environ.get("WEBHOOK_PORT", "5000")),
                             help="Port to bind the server to")
    server_parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"),
                             help="GitHub API token")
    server_parser.add_argument("--webhook-secret", default=os.environ.get("WEBHOOK_SECRET"),
                             help="Secret for validating webhook payloads")
    server_parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    server_parser.add_argument("--verbose", "-v", action="store_true",
                             help="Enable verbose logging")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    # Check if a command was specified
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check if GitHub token is provided
    if not args.github_token:
        logger.error("GitHub token is required")
        parser.print_help()
        sys.exit(1)
    
    # Run the specified command
    if args.command == "analyze":
        try:
            results = analyze_pr(
                github_token=args.github_token,
                repo=args.repo,
                pr_number=args.pr_number,
                post_comment=args.post_comment
            )
            
            # Print results summary
            print(f"Analysis results for PR #{args.pr_number} in {args.repo}:")
            print(f"Total issues: {len(results['issues'])}")
            print(f"Errors: {len([i for i in results['issues'] if i['severity'] == 'error'])}")
            print(f"Warnings: {len([i for i in results['issues'] if i['severity'] == 'warning'])}")
            print(f"Info: {len([i for i in results['issues'] if i['severity'] == 'info'])}")
            
            if args.verbose:
                import json
                print(json.dumps(results, indent=2))
        except Exception as e:
            logger.error(f"Error analyzing PR: {e}")
            sys.exit(1)
    
    elif args.command == "server":
        try:
            run_webhook_server(
                github_token=args.github_token,
                webhook_secret=args.webhook_secret,
                host=args.host,
                port=args.port,
                debug=args.debug
            )
        except Exception as e:
            logger.error(f"Error running webhook server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

