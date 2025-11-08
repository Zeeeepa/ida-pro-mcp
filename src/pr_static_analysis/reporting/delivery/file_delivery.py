"""
File delivery channel for PR static analysis reports.

This module provides the FileDelivery class for saving reports to files.
"""

from typing import Dict, Any, Optional
from .base_delivery import BaseDelivery

class FileDelivery(BaseDelivery):
    """Delivery channel for files."""
    
    def deliver(self, report: str, **kwargs) -> bool:
        """
        Deliver a report to a file.
        
        Args:
            report: Report content
            **kwargs: Additional arguments for the delivery
                file_path: Path to the output file
                mode: File open mode (default: "w")
            
        Returns:
            True if delivery was successful, False otherwise
        """
        file_path = kwargs.get("file_path")
        mode = kwargs.get("mode", "w")
        
        if not file_path:
            self.logger.error("File path is required")
            return False
            
        try:
            with open(file_path, mode) as f:
                f.write(report)
            self.logger.info(f"Report delivered to file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error delivering report to file: {e}")
            return False

