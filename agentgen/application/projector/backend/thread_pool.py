"""Thread pool for the projector application."""

import os
import logging
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable


class ThreadPool:
    """Thread pool for the projector application."""
    
    def __init__(self, max_threads: int = 10):
        """
        Initialize the thread pool.
        
        Args:
            max_threads: Maximum number of threads
        """
        self.max_threads = max(1, min(max_threads, 20))  # Limit to 1-20 threads
        self.logger = logging.getLogger(__name__)
        self.task_queue = queue.Queue()
        self.threads = []
        self.running = True
        
        # Start worker threads
        for i in range(self.max_threads):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self.threads.append(thread)
        
        self.logger.info(f"Started thread pool with {self.max_threads} threads")
    
    def _worker(self) -> None:
        """Worker thread function."""
        while self.running:
            try:
                # Get a task from the queue
                task = self.task_queue.get(timeout=1.0)
                
                if task is None:
                    # None is a signal to stop the thread
                    self.task_queue.task_done()
                    break
                
                # Unpack the task
                func, args, kwargs = task
                
                # Execute the task
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error executing task: {e}")
                
                # Mark the task as done
                self.task_queue.task_done()
            
            except queue.Empty:
                # No tasks in the queue, continue waiting
                continue
    
    def submit(self, func: Callable, *args, **kwargs) -> None:
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        if not self.running:
            self.logger.warning("Thread pool is shutting down, cannot submit new tasks")
            return
        
        # Add the task to the queue
        self.task_queue.put((func, args, kwargs))
        
        self.logger.debug(f"Submitted task {func.__name__} to thread pool")
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shut down the thread pool.
        
        Args:
            wait: Whether to wait for all tasks to complete
        """
        self.logger.info("Shutting down thread pool")
        
        # Signal that we're shutting down
        self.running = False
        
        if wait:
            # Wait for all tasks to complete
            self.task_queue.join()
        
        # Signal all threads to stop
        for _ in range(len(self.threads)):
            self.task_queue.put(None)
        
        # Wait for all threads to stop
        for thread in self.threads:
            thread.join()
        
        self.logger.info("Thread pool shut down")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the thread pool.
        
        Returns:
            Dictionary with thread pool statistics
        """
        return {
            "max_threads": self.max_threads,
            "active_threads": sum(1 for thread in self.threads if thread.is_alive()),
            "queue_size": self.task_queue.qsize(),
            "running": self.running
        }