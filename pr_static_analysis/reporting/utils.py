"""
Utility functions for PR static analysis reporting.
"""
import os
import re
import logging
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def create_temp_file(content: str, prefix: str = "report_", suffix: str = ".txt") -> str:
    """Create a temporary file with the given content.
    
    Args:
        content: Content to write to the file
        prefix: Prefix for the temporary file name
        suffix: Suffix for the temporary file name
        
    Returns:
        Path to the temporary file
    """
    try:
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path
    except Exception as e:
        logger.error(f"Failed to create temporary file: {e}")
        return ""


def format_timestamp(timestamp: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format an ISO timestamp string.
    
    Args:
        timestamp: ISO format timestamp string
        format_str: Output format string
        
    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"Failed to format timestamp: {e}")
        return timestamp


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add to truncated text
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_file_extension(file_path: str) -> str:
    """Extract the file extension from a path.
    
    Args:
        file_path: File path
        
    Returns:
        File extension (without the dot)
    """
    _, ext = os.path.splitext(file_path)
    return ext.lstrip('.').lower()


def group_results_by_file(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group analysis results by file.
    
    Args:
        results: List of analysis results
        
    Returns:
        Dict mapping file paths to lists of results
    """
    grouped = {}
    
    for result in results:
        file_path = result.get('file', 'unknown')
        
        if file_path not in grouped:
            grouped[file_path] = []
            
        grouped[file_path].append(result)
    
    return grouped


def group_results_by_severity(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group analysis results by severity.
    
    Args:
        results: List of analysis results
        
    Returns:
        Dict mapping severity levels to lists of results
    """
    grouped = {
        'error': [],
        'warning': [],
        'info': []
    }
    
    for result in results:
        severity = result.get('severity', 'info')
        
        if severity in grouped:
            grouped[severity].append(result)
        else:
            grouped['info'].append(result)
    
    return grouped


def extract_repo_info_from_url(url: str) -> tuple:
    """Extract repository owner and name from a GitHub URL.
    
    Args:
        url: GitHub URL
        
    Returns:
        Tuple of (owner, repo)
    """
    # Match patterns like https://github.com/owner/repo or github.com/owner/repo
    pattern = r'(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, url)
    
    if match:
        return match.group(1), match.group(2)
    
    return None, None

