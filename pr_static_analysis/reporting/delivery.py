"""
Delivery components for PR static analysis reports.

This module provides functionality to deliver reports to different output channels.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ReportDeliveryChannel(ABC):
    """Base class for report delivery channels."""
    
    @abstractmethod
    def deliver_report(self, report: Dict[str, Any], formatted_report: str) -> bool:
        """Deliver a report to the channel.
        
        Args:
            report: The raw report data
            formatted_report: The formatted report content
            
        Returns:
            True if delivery was successful, False otherwise
        """
        pass


class GitHubPRCommentDelivery(ReportDeliveryChannel):
    """Delivery channel for GitHub PR comments."""
    
    def __init__(self, github_client):
        """Initialize the delivery channel.
        
        Args:
            github_client: GitHub client for API access
        """
        self.github_client = github_client
    
    def deliver_report(self, report: Dict[str, Any], formatted_report: str) -> bool:
        """Deliver a report as a GitHub PR comment.
        
        Args:
            report: The raw report data
            formatted_report: The formatted report content
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            pr_number = report['pr']['number']
            repo_owner, repo_name = self._extract_repo_info(report['pr']['url'])
            
            # Create or update comment
            comment_id = self._find_existing_comment(repo_owner, repo_name, pr_number)
            
            if comment_id:
                # Update existing comment
                self.github_client.update_pr_comment(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    comment_id=comment_id,
                    body=formatted_report
                )
                logger.info(f"Updated PR comment {comment_id} for PR #{pr_number}")
            else:
                # Create new comment
                self.github_client.create_pr_comment(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    pr_number=pr_number,
                    body=formatted_report
                )
                logger.info(f"Created new PR comment for PR #{pr_number}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to deliver report to GitHub PR: {e}")
            return False
    
    def _extract_repo_info(self, pr_url: str) -> tuple:
        """Extract repository owner and name from PR URL.
        
        Args:
            pr_url: URL of the PR
            
        Returns:
            Tuple of (repo_owner, repo_name)
        """
        # Example URL: https://github.com/owner/repo/pull/123
        parts = pr_url.split('/')
        return parts[3], parts[4]
    
    def _find_existing_comment(self, repo_owner: str, repo_name: str, pr_number: int) -> Optional[int]:
        """Find existing analysis report comment.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            
        Returns:
            Comment ID if found, None otherwise
        """
        comments = self.github_client.get_pr_comments(
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number
        )
        
        # Look for comments that start with our header
        for comment in comments:
            if comment['body'].startswith('# PR Analysis Report for'):
                return comment['id']
        
        return None


class FileSystemDelivery(ReportDeliveryChannel):
    """Delivery channel for the file system."""
    
    def __init__(self, output_dir: str):
        """Initialize the delivery channel.
        
        Args:
            output_dir: Directory to write reports to
        """
        self.output_dir = output_dir
    
    def deliver_report(self, report: Dict[str, Any], formatted_report: str) -> bool:
        """Deliver a report to the file system.
        
        Args:
            report: The raw report data
            formatted_report: The formatted report content
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            import os
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Generate filename
            pr_number = report['pr']['number']
            timestamp = report['timestamp'].replace(':', '-').replace('.', '-')
            filename = f"pr_{pr_number}_analysis_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            # Write report to file
            with open(filepath, 'w') as f:
                f.write(formatted_report)
                
            logger.info(f"Report saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to deliver report to file system: {e}")
            return False


class EmailDelivery(ReportDeliveryChannel):
    """Delivery channel for email."""
    
    def __init__(self, smtp_config: Dict[str, Any], recipients: list):
        """Initialize the delivery channel.
        
        Args:
            smtp_config: SMTP configuration
            recipients: List of email recipients
        """
        self.smtp_config = smtp_config
        self.recipients = recipients
    
    def deliver_report(self, report: Dict[str, Any], formatted_report: str) -> bool:
        """Deliver a report via email.
        
        Args:
            report: The raw report data
            formatted_report: The formatted report content
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f"PR Analysis Report for #{report['pr']['number']}: {report['pr']['title']}"
            msg['From'] = self.smtp_config['sender']
            msg['To'] = ', '.join(self.recipients)
            
            # Attach report
            msg.attach(MIMEText(formatted_report, 'html' if '<html>' in formatted_report else 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                if self.smtp_config.get('use_tls', False):
                    server.starttls()
                
                if 'username' in self.smtp_config and 'password' in self.smtp_config:
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                
                server.send_message(msg)
            
            logger.info(f"Report sent via email to {', '.join(self.recipients)}")
            return True
        except Exception as e:
            logger.error(f"Failed to deliver report via email: {e}")
            return False


class ReportDeliveryService:
    """Service for delivering reports to multiple channels."""
    
    def __init__(self):
        """Initialize the delivery service."""
        self.channels = []
    
    def add_channel(self, channel: ReportDeliveryChannel):
        """Add a delivery channel.
        
        Args:
            channel: The delivery channel to add
        """
        self.channels.append(channel)
    
    def deliver_report(self, report: Dict[str, Any], formatted_report: str) -> Dict[str, bool]:
        """Deliver a report to all channels.
        
        Args:
            report: The raw report data
            formatted_report: The formatted report content
            
        Returns:
            Dict mapping channel class names to delivery success status
        """
        results = {}
        
        for channel in self.channels:
            channel_name = channel.__class__.__name__
            success = channel.deliver_report(report, formatted_report)
            results[channel_name] = success
            
        return results

