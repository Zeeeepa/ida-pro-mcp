import os
import tempfile
import unittest
import time
import uuid
import json
from pathlib import Path

from .notification_service import NotificationService, Notification, get_notification_service

class TestNotification(unittest.TestCase):
    """Tests for the Notification class."""
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification(
            id="test-id",
            message="Test message",
            source="test"
        )
        
        self.assertEqual(notification.id, "test-id")
        self.assertEqual(notification.message, "Test message")
        self.assertEqual(notification.source, "test")
        self.assertFalse(notification.read)
        self.assertIsNotNone(notification.timestamp)
    
    def test_notification_serialization(self):
        """Test serializing and deserializing a notification."""
        original = Notification(
            id="test-id",
            message="Test message",
            timestamp=1620000000.0,
            read=True,
            source="test",
            metadata={"key": "value"}
        )
        
        # Convert to dict and back
        data = original.to_dict()
        recreated = Notification.from_dict(data)
        
        # Check all properties match
        self.assertEqual(recreated.id, original.id)
        self.assertEqual(recreated.message, original.message)
        self.assertEqual(recreated.timestamp, original.timestamp)
        self.assertEqual(recreated.read, original.read)
        self.assertEqual(recreated.source, original.source)
        self.assertEqual(recreated.metadata, original.metadata)


class TestNotificationService(unittest.TestCase):
    """Tests for the NotificationService class."""
    
    def setUp(self):
        """Set up a temporary notification service for testing."""
        # Create a temporary file for storage
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Create service with the temporary file
        self.service = NotificationService(self.temp_file.name)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_notification(self):
        """Test adding a notification."""
        notification = Notification(
            id="test-id",
            message="Test message"
        )
        
        self.service.add_notification(notification)
        
        # Check notification was added
        self.assertEqual(len(self.service.get_all_notifications()), 1)
        self.assertEqual(self.service.get_notification("test-id"), notification)
    
    def test_get_unread_count(self):
        """Test getting the unread count."""
        # Add some notifications
        self.service.add_notification(Notification(
            id="read",
            message="Read notification",
            read=True
        ))
        
        self.service.add_notification(Notification(
            id="unread1",
            message="Unread notification 1"
        ))
        
        self.service.add_notification(Notification(
            id="unread2",
            message="Unread notification 2"
        ))
        
        # Check unread count
        self.assertEqual(self.service.get_unread_count(), 2)
    
    def test_mark_as_read(self):
        """Test marking a notification as read."""
        # Add an unread notification
        self.service.add_notification(Notification(
            id="test-id",
            message="Test message"
        ))
        
        # Initial unread count should be 1
        self.assertEqual(self.service.get_unread_count(), 1)
        
        # Mark as read
        result = self.service.mark_as_read("test-id")
        
        # Check result and updated unread count
        self.assertTrue(result)
        self.assertEqual(self.service.get_unread_count(), 0)
        
        # Check notification is now marked as read
        notification = self.service.get_notification("test-id")
        self.assertTrue(notification.read)
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read."""
        # Add some unread notifications
        self.service.add_notification(Notification(
            id="unread1",
            message="Unread notification 1"
        ))
        
        self.service.add_notification(Notification(
            id="unread2",
            message="Unread notification 2"
        ))
        
        # Initial unread count should be 2
        self.assertEqual(self.service.get_unread_count(), 2)
        
        # Mark all as read
        count = self.service.mark_all_as_read()
        
        # Check result and updated unread count
        self.assertEqual(count, 2)
        self.assertEqual(self.service.get_unread_count(), 0)
    
    def test_delete_notification(self):
        """Test deleting a notification."""
        # Add a notification
        self.service.add_notification(Notification(
            id="test-id",
            message="Test message"
        ))
        
        # Initial count should be 1
        self.assertEqual(len(self.service.get_all_notifications()), 1)
        
        # Delete the notification
        result = self.service.delete_notification("test-id")
        
        # Check result and updated count
        self.assertTrue(result)
        self.assertEqual(len(self.service.get_all_notifications()), 0)
    
    def test_persistence(self):
        """Test that notifications are persisted to storage."""
        # Add a notification
        self.service.add_notification(Notification(
            id="test-id",
            message="Test message",
            timestamp=1620000000.0
        ))
        
        # Create a new service instance with the same storage path
        new_service = NotificationService(self.temp_file.name)
        
        # Check that the notification was loaded
        self.assertEqual(len(new_service.get_all_notifications()), 1)
        
        notification = new_service.get_notification("test-id")
        self.assertEqual(notification.id, "test-id")
        self.assertEqual(notification.message, "Test message")
        self.assertEqual(notification.timestamp, 1620000000.0)
    
    def test_observer_notification(self):
        """Test that observers are notified of changes."""
        # Track observer calls
        observer_called = [0]
        
        def observer():
            observer_called[0] += 1
        
        # Add observer
        self.service.add_observer(observer)
        
        # Add a notification (should trigger observer)
        self.service.add_notification(Notification(
            id="test-id",
            message="Test message"
        ))
        
        # Check observer was called
        self.assertEqual(observer_called[0], 1)
        
        # Mark as read (should trigger observer)
        self.service.mark_as_read("test-id")
        
        # Check observer was called again
        self.assertEqual(observer_called[0], 2)
        
        # Remove observer
        self.service.remove_observer(observer)
        
        # Delete notification (should not trigger observer)
        self.service.delete_notification("test-id")
        
        # Check observer was not called
        self.assertEqual(observer_called[0], 2)


def run_tests():
    """Run the notification tests."""
    unittest.main(module=__name__, exit=False)


if __name__ == "__main__":
    run_tests()

