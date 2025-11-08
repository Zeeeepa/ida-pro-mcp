"""
Email delivery channel for PR static analysis reports.

This module provides the EmailDelivery class for sending reports via email.
"""

from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .base_delivery import BaseDelivery

class EmailDelivery(BaseDelivery):
    """Delivery channel for email."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None, use_tls: bool = True):
        """
        Initialize the email delivery channel.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS
        """
        super().__init__()
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        
    def deliver(self, report: str, **kwargs) -> bool:
        """
        Deliver a report via email.
        
        Args:
            report: Report content
            **kwargs: Additional arguments for the delivery
                from_addr: Sender email address
                to_addr: Recipient email address (or list of addresses)
                subject: Email subject
                is_html: Whether the report is HTML
                cc: CC recipients
                bcc: BCC recipients
            
        Returns:
            True if delivery was successful, False otherwise
        """
        from_addr = kwargs.get("from_addr")
        to_addr = kwargs.get("to_addr")
        subject = kwargs.get("subject", "PR Analysis Report")
        is_html = kwargs.get("is_html", False)
        cc = kwargs.get("cc")
        bcc = kwargs.get("bcc")
        
        if not from_addr or not to_addr:
            self.logger.error("Sender and recipient email addresses are required")
            return False
            
        if not self.smtp_server or not self.smtp_port:
            self.logger.error("SMTP server and port are required")
            return False
            
        try:
            # Create the email
            msg = MIMEMultipart()
            msg["From"] = from_addr
            
            # Handle multiple recipients
            if isinstance(to_addr, list):
                msg["To"] = ", ".join(to_addr)
            else:
                msg["To"] = to_addr
                
            msg["Subject"] = subject
            
            # Add CC if provided
            if cc:
                if isinstance(cc, list):
                    msg["Cc"] = ", ".join(cc)
                else:
                    msg["Cc"] = cc
                    
            # Add BCC if provided (not included in headers)
            if bcc and not isinstance(bcc, list):
                bcc = [bcc]
            
            # Attach the report
            if is_html:
                msg.attach(MIMEText(report, "html"))
            else:
                msg.attach(MIMEText(report, "plain"))
                
            # Prepare recipients list for sending
            recipients = []
            if isinstance(to_addr, list):
                recipients.extend(to_addr)
            else:
                recipients.append(to_addr)
                
            if cc:
                if isinstance(cc, list):
                    recipients.extend(cc)
                else:
                    recipients.append(cc)
                    
            if bcc:
                recipients.extend(bcc)
                
            # Send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                    
                if self.username and self.password:
                    server.login(self.username, self.password)
                    
                server.sendmail(from_addr, recipients, msg.as_string())
                
            self.logger.info(f"Report delivered via email to: {to_addr}")
            return True
        except Exception as e:
            self.logger.error(f"Error delivering report via email: {e}")
            return False

