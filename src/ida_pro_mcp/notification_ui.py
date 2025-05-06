import os
import sys
import threading
import time
from typing import Callable, List, Optional

import ida_kernwin
import idaapi

from .notification_service import get_notification_service, Notification

# Check if we're running in IDA Pro
try:
    import ida_kernwin
    import idaapi
    IN_IDA = True
except ImportError:
    IN_IDA = False


class NotificationBadge:
    """UI component for displaying a notification badge with unread count."""
    
    # Update interval in seconds
    UPDATE_INTERVAL = 1.0
    
    def __init__(self):
        """Initialize the notification badge."""
        self._notification_service = get_notification_service()
        self._notification_service.add_observer(self._on_notifications_changed)
        self._unread_count = self._notification_service.get_unread_count()
        self._visible = self._unread_count > 0
        self._update_timer = None
        self._lock = threading.RLock()
        
        # Start update timer
        self._start_update_timer()
    
    def _start_update_timer(self):
        """Start the timer for periodic UI updates."""
        if not IN_IDA:
            return
        
        with self._lock:
            if self._update_timer is not None:
                return
            
            self._update_timer = threading.Timer(self.UPDATE_INTERVAL, self._update_timer_callback)
            self._update_timer.daemon = True
            self._update_timer.start()
    
    def _update_timer_callback(self):
        """Callback for the update timer."""
        try:
            self._update_badge()
        finally:
            # Restart timer for next update
            with self._lock:
                self._update_timer = None
                self._start_update_timer()
    
    def _on_notifications_changed(self):
        """Callback when notifications change."""
        self._update_badge()
    
    def _update_badge(self):
        """Update the badge UI based on current unread count."""
        if not IN_IDA:
            return
        
        # Get current unread count
        unread_count = self._notification_service.get_unread_count()
        
        # Check if count changed
        if unread_count == self._unread_count:
            return
        
        self._unread_count = unread_count
        self._visible = unread_count > 0
        
        # Update UI in the main thread
        ida_kernwin.execute_ui_requests((
            (self._update_badge_ui, []),
        ))
    
    def _update_badge_ui(self):
        """Update the badge UI in the main thread."""
        # This would be implemented differently depending on how we want to display the badge
        # For now, we'll just print to the output window
        if self._visible:
            print(f"[MCP] You have {self._unread_count} unread notification(s)")
    
    def show_notifications_panel(self):
        """Show the notifications panel."""
        # This would open a panel showing all notifications
        # For now, we'll just print them to the output window
        notifications = self._notification_service.get_all_notifications()
        
        print("\n[MCP] Notifications:")
        print("=" * 50)
        
        if not notifications:
            print("No notifications")
        else:
            for notification in notifications:
                status = "UNREAD" if not notification.read else "read"
                print(f"[{status}] {notification.message}")
        
        print("=" * 50)
    
    def cleanup(self):
        """Clean up resources."""
        with self._lock:
            if self._update_timer is not None:
                self._update_timer.cancel()
                self._update_timer = None
            
            self._notification_service.remove_observer(self._on_notifications_changed)


class NotificationPanel(ida_kernwin.Form):
    """Panel for displaying and managing notifications."""
    
    def __init__(self):
        """Initialize the notification panel."""
        self._notification_service = get_notification_service()
        
        # Form definition
        form_str = """BUTTON YES* Close
BUTTON CANCEL Cancel
Notifications

<Notifications:{notifications}>
<##Mark all as read:{mark_all_as_read}>
"""
        super().__init__(form_str, {
            'notifications': ida_kernwin.Form.MultiLineTextControl(),
            'mark_all_as_read': ida_kernwin.Form.ButtonInput(self._on_mark_all_as_read),
        })
        
        # Register for notification updates
        self._notification_service.add_observer(self._on_notifications_changed)
        
        # Initial update
        self._update_notifications_list()
    
    def _update_notifications_list(self):
        """Update the notifications list in the UI."""
        notifications = self._notification_service.get_all_notifications()
        
        text = ""
        for notification in notifications:
            status = "[UNREAD] " if not notification.read else "[read] "
            text += status + notification.message + "\n"
        
        if not text:
            text = "No notifications"
        
        self.controls.notifications.value = text
    
    def _on_notifications_changed(self):
        """Callback when notifications change."""
        # Update UI in the main thread
        ida_kernwin.execute_ui_requests((
            (self._update_notifications_list, []),
        ))
    
    def _on_mark_all_as_read(self, code):
        """Callback when 'Mark all as read' button is clicked."""
        self._notification_service.mark_all_as_read()
        return 1
    
    def OnClose(self, code):
        """Called when the form is closed."""
        self._notification_service.remove_observer(self._on_notifications_changed)
        return super().OnClose(code)


# Singleton instance for the notification badge
_notification_badge = None

def get_notification_badge():
    """
    Get the global notification badge instance.
    
    Returns:
        The global notification badge instance
    """
    global _notification_badge
    if _notification_badge is None:
        _notification_badge = NotificationBadge()
    
    return _notification_badge


def show_notification_panel():
    """Show the notification panel."""
    if not IN_IDA:
        return
    
    panel = NotificationPanel()
    panel.Compile()
    panel.Execute()


def cleanup_notification_ui():
    """Clean up notification UI resources."""
    global _notification_badge
    if _notification_badge is not None:
        _notification_badge.cleanup()
        _notification_badge = None

