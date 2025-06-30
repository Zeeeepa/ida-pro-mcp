"""
Base Delivery Module

This module provides the base delivery interface for report delivery channels.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDelivery(ABC):
    """
    Base class for report delivery channels.
    
    This abstract class defines the interface for report delivery channels.
    All delivery channels should inherit from this class and implement the deliver method.
    """
    
    @abstractmethod
    def deliver(self, report: str, **kwargs) -> bool:
        """
        Deliver a report through the channel.
        
        Args:
            report: The report to deliver
            **kwargs: Additional delivery-specific arguments
            
        Returns:
            True if delivery was successful, False otherwise
        """
        pass

