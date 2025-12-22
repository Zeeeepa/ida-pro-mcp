"""
Delivery mechanisms for PR static analysis reports.

This module contains functions for delivering reports to different destinations,
such as GitHub comments, files, and web servers.
"""

import os
import json
from typing import Any, Dict, Optional, Union
import tempfile
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

# Try to import GitHub libraries, but provide fallbacks if not available
try:
    from github import Github, GithubException
    HAS_GITHUB_LIBS = True
except ImportError:
    HAS_GITHUB_LIBS = False

from .report_generator import Report
from .report_formatter import HTMLFormatter, MarkdownFormatter, JSONFormatter


def post_report_as_comment(repo: str, pr_number: int, report: Report) -> Optional[str]:
    """
    Post a report as a PR comment.
    
    Args:
        repo: The repository name (owner/repo).
        pr_number: The PR number.
        report: The report to post.
        
    Returns:
        The URL of the comment, or None if posting failed.
    """
    if not HAS_GITHUB_LIBS:
        return _get_github_fallback("post_report_as_comment", repo, pr_number)
    
    try:
        # Format report as Markdown
        formatter = MarkdownFormatter()
        md_report = formatter.format_report(report)
        
        # Truncate if too long (GitHub has a comment size limit)
        if len(md_report) > 65000:
            md_report = md_report[:65000] + "\n\n... (report truncated due to size limits)"
        
        # Get GitHub token from environment
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return None
        
        # Create GitHub client
        g = Github(token)
        
        # Get repository
        github_repo = g.get_repo(repo)
        
        # Get pull request
        pr = github_repo.get_pull(pr_number)
        
        # Create comment
        comment = pr.create_issue_comment(md_report)
        
        return comment.html_url
    
    except Exception as e:
        print(f"Error posting report as comment: {e}")
        return None


def post_report_as_review(repo: str, pr_number: int, report: Report) -> Optional[str]:
    """
    Post a report as a PR review.
    
    Args:
        repo: The repository name (owner/repo).
        pr_number: The PR number.
        report: The report to post.
        
    Returns:
        The URL of the review, or None if posting failed.
    """
    if not HAS_GITHUB_LIBS:
        return _get_github_fallback("post_report_as_review", repo, pr_number)
    
    try:
        # Format report as Markdown
        formatter = MarkdownFormatter()
        md_report = formatter.format_report(report)
        
        # Truncate if too long (GitHub has a review size limit)
        if len(md_report) > 65000:
            md_report = md_report[:65000] + "\n\n... (report truncated due to size limits)"
        
        # Get GitHub token from environment
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return None
        
        # Create GitHub client
        g = Github(token)
        
        # Get repository
        github_repo = g.get_repo(repo)
        
        # Get pull request
        pr = github_repo.get_pull(pr_number)
        
        # Create review
        review = pr.create_review(body=md_report, event="COMMENT")
        
        return review.html_url
    
    except Exception as e:
        print(f"Error posting report as review: {e}")
        return None


def post_report_as_check(repo: str, commit_sha: str, report: Report) -> Optional[str]:
    """
    Post a report as a check run.
    
    Args:
        repo: The repository name (owner/repo).
        commit_sha: The commit SHA.
        report: The report to post.
        
    Returns:
        The URL of the check run, or None if posting failed.
    """
    if not HAS_GITHUB_LIBS:
        return _get_github_fallback("post_report_as_check", repo, commit_sha)
    
    try:
        # Format report as Markdown
        formatter = MarkdownFormatter()
        md_report = formatter.format_report(report)
        
        # Truncate if too long (GitHub has a check output size limit)
        if len(md_report) > 65000:
            md_report = md_report[:65000] + "\n\n... (report truncated due to size limits)"
        
        # Get GitHub token from environment
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return None
        
        # Create GitHub client
        g = Github(token)
        
        # Get repository
        github_repo = g.get_repo(repo)
        
        # Determine check conclusion based on report results
        conclusion = "success"
        for result in report.results:
            if result.severity in ["critical", "error"]:
                conclusion = "failure"
                break
            elif result.severity == "warning" and conclusion != "failure":
                conclusion = "neutral"
        
        # Create check run
        check_run = github_repo.create_check_run(
            name="PR Static Analysis",
            head_sha=commit_sha,
            status="completed",
            conclusion=conclusion,
            output={
                "title": report.title,
                "summary": report.summary,
                "text": md_report
            }
        )
        
        return check_run.html_url
    
    except Exception as e:
        print(f"Error posting report as check: {e}")
        return None


def save_report_to_file(report: Report, file_path: str, format: str = "html") -> bool:
    """
    Save a report to a file.
    
    Args:
        report: The report to save.
        file_path: The path to save the report to.
        format: The format to save the report in ("html", "markdown", or "json").
        
    Returns:
        True if the report was saved successfully, False otherwise.
    """
    try:
        # Format report
        if format.lower() == "html":
            formatter = HTMLFormatter()
        elif format.lower() == "markdown":
            formatter = MarkdownFormatter()
        elif format.lower() == "json":
            formatter = JSONFormatter()
        else:
            print(f"Unsupported format: {format}")
            return False
        
        formatted_report = formatter.format_report(report)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Write report to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_report)
        
        return True
    
    except Exception as e:
        print(f"Error saving report to file: {e}")
        return False


def save_report_to_directory(report: Report, directory: str) -> Dict[str, str]:
    """
    Save a report to a directory in multiple formats.
    
    Args:
        report: The report to save.
        directory: The directory to save the report to.
        
    Returns:
        A dictionary mapping format names to file paths.
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate a base filename from the report title
        base_filename = report.title.lower().replace(" ", "_")
        
        # Save in different formats
        file_paths = {}
        
        # HTML
        html_path = os.path.join(directory, f"{base_filename}.html")
        if save_report_to_file(report, html_path, "html"):
            file_paths["html"] = html_path
        
        # Markdown
        md_path = os.path.join(directory, f"{base_filename}.md")
        if save_report_to_file(report, md_path, "markdown"):
            file_paths["markdown"] = md_path
        
        # JSON
        json_path = os.path.join(directory, f"{base_filename}.json")
        if save_report_to_file(report, json_path, "json"):
            file_paths["json"] = json_path
        
        return file_paths
    
    except Exception as e:
        print(f"Error saving report to directory: {e}")
        return {}


class ReportHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for serving reports."""
    
    def __init__(self, *args, report_content=None, **kwargs):
        self.report_content = report_content
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.report_content.encode("utf-8"))
        else:
            super().do_GET()


def serve_report(report: Report, port: int = 8000) -> Optional[str]:
    """
    Serve a report via a web server.
    
    Args:
        report: The report to serve.
        port: The port to serve the report on.
        
    Returns:
        The URL of the report, or None if serving failed.
    """
    try:
        # Format report as HTML
        formatter = HTMLFormatter()
        html_report = formatter.format_report(report)
        
        # Create a temporary directory for serving static files
        temp_dir = tempfile.mkdtemp()
        
        # Create a custom request handler with the report content
        handler = lambda *args, **kwargs: ReportHTTPRequestHandler(
            *args, report_content=html_report, **kwargs
        )
        
        # Create and start the server
        server = socketserver.TCPServer(("", port), handler)
        
        # Start the server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Open the report in a web browser
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        
        print(f"Report server started at {url}")
        print("Press Ctrl+C to stop the server")
        
        return url
    
    except Exception as e:
        print(f"Error serving report: {e}")
        return None


def create_report_url(report: Report) -> Optional[str]:
    """
    Create a URL for a report.
    
    This is a placeholder implementation that saves the report to a temporary file
    and returns a file:// URL. In a real implementation, this would upload the report
    to a web server or cloud storage and return the URL.
    
    Args:
        report: The report to create a URL for.
        
    Returns:
        The URL of the report, or None if creation failed.
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            # Format report as HTML
            formatter = HTMLFormatter()
            html_report = formatter.format_report(report)
            
            # Write report to file
            f.write(html_report.encode("utf-8"))
            
            # Get file path
            file_path = f.name
        
        # Convert file path to URL
        file_url = Path(file_path).as_uri()
        
        return file_url
    
    except Exception as e:
        print(f"Error creating report URL: {e}")
        return None


def _get_github_fallback(function_name: str, *args) -> Optional[str]:
    """
    Get a fallback message when GitHub libraries are not available.
    
    Args:
        function_name: The name of the function that was called.
        *args: The arguments that were passed to the function.
        
    Returns:
        A message indicating that GitHub libraries are not available.
    """
    print(f"GitHub libraries are not available. Cannot call {function_name}({', '.join(map(str, args))}).")
    return None

