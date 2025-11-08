"""
Slack Delivery Module

This module provides a delivery channel for sending reports to Slack.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union

from .base_delivery import BaseDelivery

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class SlackDelivery(BaseDelivery):
    """
    Delivery channel for sending reports to Slack.
    
    This delivery channel can send reports as messages to Slack channels or users.
    It supports both plain text and formatted messages with attachments.
    """
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        token: Optional[str] = None,
        default_channel: Optional[str] = None,
        username: Optional[str] = "PR Static Analysis Bot",
        icon_emoji: Optional[str] = ":robot_face:",
        default_blocks: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a new SlackDelivery channel.
        
        Args:
            webhook_url: Slack webhook URL (for webhook-based delivery)
            token: Slack API token (for API-based delivery)
            default_channel: Default channel or user to send messages to
            username: Username to display for the bot
            icon_emoji: Emoji to use as the bot's icon
            default_blocks: Default blocks to include in the message
            
        Note:
            Either webhook_url or token must be provided.
            
        Raises:
            ImportError: If the requests package is not installed
            ValueError: If neither webhook_url nor token is provided
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "The requests package is required for SlackDelivery. "
                "Install it with: pip install requests"
            )
        
        if not webhook_url and not token:
            raise ValueError("Either webhook_url or token must be provided")
        
        self.webhook_url = webhook_url
        self.token = token
        self.default_channel = default_channel
        self.username = username
        self.icon_emoji = icon_emoji
        self.default_blocks = default_blocks
        
    def deliver(
        self, 
        report: str, 
        **kwargs
    ) -> bool:
        """
        Deliver a report to Slack.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments, including:
                - channel: Channel or user to send the message to
                - username: Username to display for the bot
                - icon_emoji: Emoji to use as the bot's icon
                - blocks: Blocks to include in the message
                - attachments: Attachments to include in the message
                - thread_ts: Thread timestamp to reply to
                - unfurl_links: Whether to unfurl links in the message
                - unfurl_media: Whether to unfurl media in the message
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            # Determine the delivery method
            if self.webhook_url:
                return self._deliver_via_webhook(report, **kwargs)
            else:
                return self._deliver_via_api(report, **kwargs)
        
        except Exception as e:
            logging.error(f"Error delivering report to Slack: {e}")
            return False
    
    def _deliver_via_webhook(self, report: str, **kwargs) -> bool:
        """
        Deliver a report to Slack using a webhook.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments
            
        Returns:
            True if delivery was successful, False otherwise
        """
        # Get message parameters
        channel = kwargs.get('channel', self.default_channel)
        username = kwargs.get('username', self.username)
        icon_emoji = kwargs.get('icon_emoji', self.icon_emoji)
        blocks = kwargs.get('blocks')
        attachments = kwargs.get('attachments')
        
        # Create the message payload
        payload = {
            'text': report
        }
        
        if channel:
            payload['channel'] = channel
        
        if username:
            payload['username'] = username
        
        if icon_emoji:
            payload['icon_emoji'] = icon_emoji
        
        if blocks:
            payload['blocks'] = blocks
        elif self.default_blocks:
            payload['blocks'] = self.default_blocks
        
        if attachments:
            payload['attachments'] = attachments
        
        # Send the message
        response = requests.post(
            self.webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.status_code == 200
    
    def _deliver_via_api(self, report: str, **kwargs) -> bool:
        """
        Deliver a report to Slack using the API.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments
            
        Returns:
            True if delivery was successful, False otherwise
        """
        # Get message parameters
        channel = kwargs.get('channel', self.default_channel)
        blocks = kwargs.get('blocks')
        attachments = kwargs.get('attachments')
        thread_ts = kwargs.get('thread_ts')
        unfurl_links = kwargs.get('unfurl_links', False)
        unfurl_media = kwargs.get('unfurl_media', False)
        
        if not channel:
            raise ValueError("Channel is required for API-based delivery")
        
        # Create the message payload
        payload = {
            'token': self.token,
            'channel': channel,
            'text': report,
            'unfurl_links': unfurl_links,
            'unfurl_media': unfurl_media
        }
        
        if blocks:
            payload['blocks'] = json.dumps(blocks)
        elif self.default_blocks:
            payload['blocks'] = json.dumps(self.default_blocks)
        
        if attachments:
            payload['attachments'] = json.dumps(attachments)
        
        if thread_ts:
            payload['thread_ts'] = thread_ts
        
        # Send the message
        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            data=payload,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        response_data = response.json()
        return response_data.get('ok', False)

