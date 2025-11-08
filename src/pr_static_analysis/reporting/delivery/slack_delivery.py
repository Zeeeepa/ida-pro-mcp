"""
Slack delivery channel for PR static analysis reports.

This module provides the SlackDelivery class for posting reports to Slack.
"""

from typing import Dict, Any, Optional
import requests
from .base_delivery import BaseDelivery

class SlackDelivery(BaseDelivery):
    """Delivery channel for Slack."""
    
    def __init__(self, webhook_url: str = None, slack_client = None):
        """
        Initialize the Slack delivery channel.
        
        Args:
            webhook_url: Slack webhook URL
            slack_client: Slack client instance (alternative to webhook URL)
        """
        super().__init__()
        self.webhook_url = webhook_url
        self.slack_client = slack_client
        
    def deliver(self, report: str, **kwargs) -> bool:
        """
        Deliver a report to Slack.
        
        Args:
            report: Report content
            **kwargs: Additional arguments for the delivery
                channel: Slack channel
                username: Bot username
                icon_emoji: Bot icon emoji
                blocks: Slack blocks for rich formatting
            
        Returns:
            True if delivery was successful, False otherwise
        """
        channel = kwargs.get("channel")
        username = kwargs.get("username", "PR Analyzer")
        icon_emoji = kwargs.get("icon_emoji", ":robot_face:")
        blocks = kwargs.get("blocks")
        
        # If using the Slack client
        if self.slack_client:
            try:
                if blocks:
                    self.slack_client.chat_postMessage(
                        channel=channel,
                        blocks=blocks
                    )
                else:
                    self.slack_client.chat_postMessage(
                        channel=channel,
                        text=report,
                        username=username,
                        icon_emoji=icon_emoji
                    )
                    
                self.logger.info(f"Report delivered to Slack channel: {channel}")
                return True
            except Exception as e:
                self.logger.error(f"Error delivering report to Slack: {e}")
                return False
        
        # If using the webhook URL
        elif self.webhook_url:
            try:
                # Create the payload
                payload = {
                    "text": report,
                }
                
                if channel:
                    payload["channel"] = channel
                    
                if username:
                    payload["username"] = username
                    
                if icon_emoji:
                    payload["icon_emoji"] = icon_emoji
                    
                if blocks:
                    payload["blocks"] = blocks
                
                # Send the message
                response = requests.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
                self.logger.info(f"Report delivered to Slack")
                return True
            except Exception as e:
                self.logger.error(f"Error delivering report to Slack: {e}")
                return False
        else:
            self.logger.error("Either Slack webhook URL or Slack client is required")
            return False

