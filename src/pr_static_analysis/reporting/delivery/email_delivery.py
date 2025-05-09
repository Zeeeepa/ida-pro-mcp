"""
Email Delivery Module

This module provides a delivery channel for sending reports via email.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union

from .base_delivery import BaseDelivery


class EmailDelivery(BaseDelivery):
    """
    Delivery channel for sending reports via email.
    
    This delivery channel can send reports as email messages to specified recipients.
    It supports both plain text and HTML email formats.
    """
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        default_sender: Optional[str] = None,
        default_recipients: Optional[List[str]] = None,
        default_subject: str = "PR Static Analysis Report"
    ):
        """
        Initialize a new EmailDelivery channel.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: SMTP username (if authentication is required)
            password: SMTP password (if authentication is required)
            use_tls: Whether to use TLS encryption
            default_sender: Default sender email address
            default_recipients: Default recipient email addresses
            default_subject: Default email subject
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.default_sender = default_sender
        self.default_recipients = default_recipients or []
        self.default_subject = default_subject
        
    def deliver(
        self, 
        report: str, 
        **kwargs
    ) -> bool:
        """
        Deliver a report via email.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments, including:
                - sender: Sender email address
                - recipients: List of recipient email addresses
                - subject: Email subject
                - is_html: Whether the report is in HTML format
                - cc: List of CC recipients
                - bcc: List of BCC recipients
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            # Get email parameters
            sender = kwargs.get('sender', self.default_sender)
            recipients = kwargs.get('recipients', self.default_recipients)
            subject = kwargs.get('subject', self.default_subject)
            is_html = kwargs.get('is_html', False)
            cc = kwargs.get('cc', [])
            bcc = kwargs.get('bcc', [])
            
            if not sender:
                raise ValueError("Sender email address is required")
            
            if not recipients:
                raise ValueError("At least one recipient email address is required")
            
            # Create the email message
            msg = MIMEMultipart('alternative')
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
                recipients.extend(cc)
            
            if bcc:
                recipients.extend(bcc)
            
            # Attach the report
            if is_html:
                msg.attach(MIMEText(report, 'html'))
            else:
                msg.attach(MIMEText(report, 'plain'))
            
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.sendmail(sender, recipients, msg.as_string())
            
            return True
        
        except Exception as e:
            logging.error(f"Error delivering report via email: {e}")
            return False

