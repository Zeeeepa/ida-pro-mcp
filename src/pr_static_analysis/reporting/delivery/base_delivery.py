"""
Base delivery channel for PR static analysis reports.

This module provides the BaseDelivery class that all delivery channels should inherit from.
"""

from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

class BaseDelivery(ABC):
    """
    Base class for report delivery channels.
    
    This class provides methods for delivering reports to different destinations.
    """
    
    def __init__(self):
        """Initialize the delivery channel."""
        self.logger = logging.getLogger(__name__)
        
    @abstractmethod
    def deliver(self, report: str, **kwargs) -> bool:
        """
        Deliver a report.
        
        Args:
            report: Report content
            **kwargs: Additional arguments for the delivery
            
        Returns:
            True if delivery was successful, False otherwise
        """
        pass

