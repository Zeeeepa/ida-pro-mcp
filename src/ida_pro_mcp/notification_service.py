import time
import threading
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

class Notification:
    """Represents a single notification in the system."""
    
    def __init__(self, id: str, message: str, timestamp: float = None, read: bool = False, 
                 source: str = None, metadata: Dict[str, Any] = None):
        """
        Initialize a new notification.
        
        Args:
            id: Unique identifier for the notification
            message: The notification message text
            timestamp: Unix timestamp when the notification was created (defaults to current time)
            read: Whether the notification has been read
            source: Source of the notification (e.g., "ida", "plugin", "system")
            metadata: Additional data associated with the notification
        """
        self.id = id
        self.message = message
        self.timestamp = timestamp or time.time()
        self.read = read
        self.source = source
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the notification to a dictionary for serialization."""
        return {
            "id": self.id,
            "message": self.message,
            "timestamp": self.timestamp,
            "read": self.read,
            "source": self.source,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create a notification from a dictionary."""
        return cls(
            id=data["id"],
            message=data["message"],
            timestamp=data["timestamp"],
            read=data["read"],
            source=data.get("source"),
            metadata=data.get("metadata", {})
        )


class NotificationService:
    """Service for managing notifications."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the notification service.
        
        Args:
            storage_path: Path to store notifications (if None, uses in-memory storage only)
        """
        self._notifications: Dict[str, Notification] = {}
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._observers = []
        
        # Load existing notifications if storage path is provided
        if storage_path:
            self._load_notifications()
    
    def add_notification(self, notification: Notification) -> None:
        """
        Add a new notification.
        
        Args:
            notification: The notification to add
        """
        with self._lock:
            self._notifications[notification.id] = notification
            self._save_notifications()
            self._notify_observers()
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a notification by ID.
        
        Args:
            notification_id: ID of the notification to retrieve
            
        Returns:
            The notification if found, None otherwise
        """
        with self._lock:
            return self._notifications.get(notification_id)
    
    def get_all_notifications(self) -> List[Notification]:
        """
        Get all notifications.
        
        Returns:
            List of all notifications, sorted by timestamp (newest first)
        """
        with self._lock:
            return sorted(
                self._notifications.values(),
                key=lambda n: n.timestamp,
                reverse=True
            )
    
    def get_unread_notifications(self) -> List[Notification]:
        """
        Get all unread notifications.
        
        Returns:
            List of unread notifications, sorted by timestamp (newest first)
        """
        with self._lock:
            return sorted(
                [n for n in self._notifications.values() if not n.read],
                key=lambda n: n.timestamp,
                reverse=True
            )
    
    def get_unread_count(self) -> int:
        """
        Get the count of unread notifications.
        
        Returns:
            Number of unread notifications
        """
        with self._lock:
            return sum(1 for n in self._notifications.values() if not n.read)
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            True if the notification was found and updated, False otherwise
        """
        with self._lock:
            notification = self._notifications.get(notification_id)
            if notification and not notification.read:
                notification.read = True
                self._save_notifications()
                self._notify_observers()
                return True
            return False
    
    def mark_all_as_read(self) -> int:
        """
        Mark all notifications as read.
        
        Returns:
            Number of notifications that were marked as read
        """
        with self._lock:
            count = 0
            for notification in self._notifications.values():
                if not notification.read:
                    notification.read = True
                    count += 1
            
            if count > 0:
                self._save_notifications()
                self._notify_observers()
            
            return count
    
    def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: ID of the notification to delete
            
        Returns:
            True if the notification was found and deleted, False otherwise
        """
        with self._lock:
            if notification_id in self._notifications:
                del self._notifications[notification_id]
                self._save_notifications()
                self._notify_observers()
                return True
            return False
    
    def add_observer(self, callback):
        """
        Add an observer to be notified when notifications change.
        
        Args:
            callback: Function to call when notifications change
        """
        with self._lock:
            self._observers.append(callback)
    
    def remove_observer(self, callback):
        """
        Remove an observer.
        
        Args:
            callback: Observer function to remove
        """
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)
    
    def _notify_observers(self):
        """Notify all observers of a change in notifications."""
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                print(f"Error notifying observer: {e}")
    
    def _save_notifications(self):
        """Save notifications to storage if a storage path is configured."""
        if not self._storage_path:
            return
        
        try:
            # Ensure directory exists
            storage_dir = os.path.dirname(self._storage_path)
            if storage_dir:
                os.makedirs(storage_dir, exist_ok=True)
            
            # Convert notifications to serializable format
            data = {
                notification_id: notification.to_dict()
                for notification_id, notification in self._notifications.items()
            }
            
            # Write to file
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving notifications: {e}")
    
    def _load_notifications(self):
        """Load notifications from storage if available."""
        if not self._storage_path or not os.path.exists(self._storage_path):
            return
        
        try:
            with open(self._storage_path, 'r') as f:
                data = json.load(f)
            
            # Convert data back to Notification objects
            self._notifications = {
                notification_id: Notification.from_dict(notification_data)
                for notification_id, notification_data in data.items()
            }
        except Exception as e:
            print(f"Error loading notifications: {e}")
            # Initialize with empty dict if loading fails
            self._notifications = {}


# Singleton instance for global access
_notification_service = None

def get_notification_service(storage_path: Optional[str] = None) -> NotificationService:
    """
    Get the global notification service instance.
    
    Args:
        storage_path: Path to store notifications (only used when creating the service)
        
    Returns:
        The global notification service instance
    """
    global _notification_service
    if _notification_service is None:
        if storage_path is None:
            # Default storage path in user's home directory
            home_dir = str(Path.home())
            storage_path = os.path.join(home_dir, '.ida_pro_mcp', 'notifications.json')
        
        _notification_service = NotificationService(storage_path)
    
    return _notification_service

