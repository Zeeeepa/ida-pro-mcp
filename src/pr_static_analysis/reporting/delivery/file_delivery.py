"""
File Delivery Module

This module provides a delivery channel for saving reports to files.
"""

import logging
import os
from typing import Any, Dict, Optional

from .base_delivery import BaseDelivery


class FileDelivery(BaseDelivery):
    """
    Delivery channel for saving reports to files.
    
    This delivery channel can save reports to local files in various formats.
    """
    
    def __init__(
        self,
        default_output_dir: str = "reports",
        default_filename_template: str = "report_{timestamp}.{extension}",
        create_dirs: bool = True
    ):
        """
        Initialize a new FileDelivery channel.
        
        Args:
            default_output_dir: Default directory to save reports to
            default_filename_template: Default template for report filenames
            create_dirs: Whether to create directories if they don't exist
        """
        self.default_output_dir = default_output_dir
        self.default_filename_template = default_filename_template
        self.create_dirs = create_dirs
        
    def deliver(
        self, 
        report: str, 
        **kwargs
    ) -> bool:
        """
        Deliver a report by saving it to a file.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments, including:
                - output_dir: Directory to save the report to
                - filename: Filename for the report
                - extension: File extension for the report
                - timestamp: Timestamp to include in the filename
                - mode: File open mode (default: 'w')
                - encoding: File encoding (default: 'utf-8')
            
        Returns:
            True if delivery was successful, False otherwise
        """
        try:
            # Get file parameters
            output_dir = kwargs.get('output_dir', self.default_output_dir)
            filename = kwargs.get('filename')
            extension = kwargs.get('extension', 'txt')
            timestamp = kwargs.get('timestamp', self._get_timestamp())
            mode = kwargs.get('mode', 'w')
            encoding = kwargs.get('encoding', 'utf-8')
            
            # Create the output directory if it doesn't exist
            if self.create_dirs and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate the filename if not provided
            if not filename:
                filename = self.default_filename_template.format(
                    timestamp=timestamp,
                    extension=extension
                )
            
            # Ensure the filename has the correct extension
            if not filename.endswith(f".{extension}"):
                filename = f"{filename}.{extension}"
            
            # Create the full file path
            file_path = os.path.join(output_dir, filename)
            
            # Write the report to the file
            with open(file_path, mode, encoding=encoding) as f:
                f.write(report)
            
            logging.info(f"Report saved to {file_path}")
            return True
        
        except Exception as e:
            logging.error(f"Error delivering report to file: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """
        Get a timestamp string for use in filenames.
        
        Returns:
            A timestamp string in the format YYYYMMDD_HHMMSS
        """
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

