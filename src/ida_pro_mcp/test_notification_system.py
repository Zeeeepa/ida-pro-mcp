#!/usr/bin/env python3
"""
Test script for the notification system.
This script can be run directly to test the notification system without IDA Pro.
"""

import os
import sys
import time
import threading
import uuid
from pathlib import Path

# Add the parent directory to the path so we can import the notification modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from ida_pro_mcp.notification_service import get_notification_service, Notification

def test_notification_system():
    """Test the notification system."""
    print("Testing notification system...")
    
    # Get the notification service
    notification_service = get_notification_service()
    
    # Add some test notifications
    for i in range(5):
        notification_id = str(uuid.uuid4())
        notification = Notification(
            id=notification_id,
            message=f"Test notification {i+1}",
            source="test"
        )
        notification_service.add_notification(notification)
        print(f"Added notification: {notification.message}")
    
    # Print the unread count
    unread_count = notification_service.get_unread_count()
    print(f"Unread count: {unread_count}")
    
    # Get all notifications
    notifications = notification_service.get_all_notifications()
    print(f"All notifications ({len(notifications)}):")
    for notification in notifications:
        print(f"  - [{notification.id}] {notification.message}")
    
    # Mark one notification as read
    if notifications:
        notification_id = notifications[0].id
        notification_service.mark_as_read(notification_id)
        print(f"Marked notification {notification_id} as read")
    
    # Print the updated unread count
    unread_count = notification_service.get_unread_count()
    print(f"Updated unread count: {unread_count}")
    
    # Mark all notifications as read
    count = notification_service.mark_all_as_read()
    print(f"Marked {count} notifications as read")
    
    # Print the final unread count
    unread_count = notification_service.get_unread_count()
    print(f"Final unread count: {unread_count}")
    
    print("Notification system test completed successfully!")

def test_observer_pattern():
    """Test the observer pattern in the notification service."""
    print("Testing observer pattern...")
    
    # Get the notification service
    notification_service = get_notification_service()
    
    # Create a counter for observer calls
    observer_calls = [0]
    
    # Define an observer function
    def observer():
        observer_calls[0] += 1
        print(f"Observer called ({observer_calls[0]})")
    
    # Add the observer
    notification_service.add_observer(observer)
    print("Added observer")
    
    # Add a notification (should trigger observer)
    notification = Notification(
        id=str(uuid.uuid4()),
        message="Observer test notification",
        source="test"
    )
    notification_service.add_notification(notification)
    print(f"Added notification: {notification.message}")
    
    # Mark the notification as read (should trigger observer)
    notification_service.mark_as_read(notification.id)
    print(f"Marked notification {notification.id} as read")
    
    # Remove the observer
    notification_service.remove_observer(observer)
    print("Removed observer")
    
    # Add another notification (should not trigger observer)
    notification = Notification(
        id=str(uuid.uuid4()),
        message="Observer test notification 2",
        source="test"
    )
    notification_service.add_notification(notification)
    print(f"Added notification: {notification.message}")
    
    # Check observer calls
    print(f"Observer was called {observer_calls[0]} times")
    
    print("Observer pattern test completed!")

def test_persistence():
    """Test notification persistence."""
    print("Testing notification persistence...")
    
    # Create a temporary file for storage
    temp_dir = Path(os.path.expanduser("~")) / ".ida_pro_mcp_test"
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / "test_notifications.json"
    
    # Create a notification service with the temporary file
    notification_service = get_notification_service(str(temp_file))
    
    # Add a notification
    notification = Notification(
        id="persistence-test",
        message="Persistence test notification",
        source="test"
    )
    notification_service.add_notification(notification)
    print(f"Added notification: {notification.message}")
    
    # Create a new service instance with the same storage path
    new_service = get_notification_service(str(temp_file))
    
    # Check that the notification was loaded
    loaded_notification = new_service.get_notification("persistence-test")
    if loaded_notification:
        print(f"Successfully loaded notification: {loaded_notification.message}")
    else:
        print("Failed to load notification!")
    
    # Clean up
    if temp_file.exists():
        temp_file.unlink()
    print("Persistence test completed!")

if __name__ == "__main__":
    test_notification_system()
    print("\n" + "="*50 + "\n")
    test_observer_pattern()
    print("\n" + "="*50 + "\n")
    test_persistence()

