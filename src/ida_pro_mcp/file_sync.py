"""
File Synchronization Module for IDA Pro MCP

This module handles file operations and ensures the application has all required
files and directories, creating template files with sensible defaults for first-time users.
"""

import os
import json
import shutil
import logging
import platform
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

# Default template content
DEFAULT_TEMPLATES = {
    "comments.txt": "# IDA Pro MCP Comments\n# Add your comments here\n",
    "settings.json": json.dumps({
        "autoSave": True,
        "backupFiles": True,
        "backupInterval": 300,  # 5 minutes
        "maxBackups": 5,
        "logLevel": "INFO"
    }, indent=2),
    ".env": "# IDA Pro MCP Environment Variables\n# Add your environment variables here\n"
}

# Required directories structure
REQUIRED_DIRECTORIES = [
    "config",
    "backups",
    "templates",
    "logs"
]


def ensure_directory_exists(directory_path: Union[str, Path]) -> bool:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path: Path to the directory to create
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False


def create_template_file(file_path: Union[str, Path], content: str, overwrite: bool = False) -> bool:
    """
    Create a template file with the given content if it doesn't exist.
    
    Args:
        file_path: Path to the file to create
        content: Content to write to the file
        overwrite: Whether to overwrite the file if it already exists
        
    Returns:
        bool: True if file was created or already exists, False if creation failed
    """
    try:
        path = Path(file_path)
        
        # Create parent directory if it doesn't exist
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists and handle accordingly
        if path.exists() and not overwrite:
            logger.debug(f"File already exists (not overwriting): {path}")
            return True
        
        # Write content to file
        with open(path, 'w') as f:
            f.write(content)
        
        # Set appropriate permissions
        set_file_permissions(path)
        
        logger.info(f"Created template file: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create template file {file_path}: {str(e)}")
        return False


def set_file_permissions(file_path: Union[str, Path]) -> bool:
    """
    Set appropriate permissions for the given file based on the platform.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if permissions were set successfully, False otherwise
    """
    try:
        path = Path(file_path)
        
        # Skip if file doesn't exist
        if not path.exists():
            logger.warning(f"Cannot set permissions for non-existent file: {path}")
            return False
        
        # Set permissions based on platform
        if platform.system() != "Windows":
            # User read/write, group read, others read (644)
            os.chmod(path, 0o644)
        
        return True
    except Exception as e:
        logger.error(f"Failed to set permissions for {file_path}: {str(e)}")
        return False


def backup_file(file_path: Union[str, Path], backup_dir: Union[str, Path], max_backups: int = 5) -> Optional[Path]:
    """
    Create a backup of the specified file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store backups
        max_backups: Maximum number of backups to keep
        
    Returns:
        Optional[Path]: Path to the backup file if successful, None otherwise
    """
    try:
        source_path = Path(file_path)
        backup_path = Path(backup_dir)
        
        # Skip if source file doesn't exist
        if not source_path.exists():
            logger.warning(f"Cannot backup non-existent file: {source_path}")
            return None
        
        # Create backup directory if it doesn't exist
        if not backup_path.exists():
            backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = source_path.stat().st_mtime
        backup_filename = f"{source_path.stem}_{int(timestamp)}{source_path.suffix}"
        backup_file_path = backup_path / backup_filename
        
        # Copy the file
        shutil.copy2(source_path, backup_file_path)
        logger.info(f"Created backup: {backup_file_path}")
        
        # Clean up old backups if needed
        cleanup_old_backups(source_path.name, backup_path, max_backups)
        
        return backup_file_path
    except Exception as e:
        logger.error(f"Failed to backup file {file_path}: {str(e)}")
        return None


def cleanup_old_backups(base_filename: str, backup_dir: Union[str, Path], max_backups: int) -> int:
    """
    Remove old backups exceeding the maximum number.
    
    Args:
        base_filename: Base name of the file (without timestamp)
        backup_dir: Directory containing backups
        max_backups: Maximum number of backups to keep
        
    Returns:
        int: Number of backups removed
    """
    try:
        backup_path = Path(backup_dir)
        base_name = Path(base_filename).stem
        
        # Find all backups for this file
        backups = list(backup_path.glob(f"{base_name}_*"))
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove excess backups
        removed = 0
        if len(backups) > max_backups:
            for old_backup in backups[max_backups:]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")
                removed += 1
        
        return removed
    except Exception as e:
        logger.error(f"Failed to clean up old backups for {base_filename}: {str(e)}")
        return 0


def get_app_data_dir() -> Path:
    """
    Get the appropriate application data directory based on the platform.
    
    Returns:
        Path: Path to the application data directory
    """
    if platform.system() == "Windows":
        base_dir = Path(os.environ.get("APPDATA", ""))
        app_dir = base_dir / "IDA Pro MCP"
    elif platform.system() == "Darwin":  # macOS
        base_dir = Path.home() / "Library" / "Application Support"
        app_dir = base_dir / "IDA Pro MCP"
    else:  # Linux and others
        base_dir = Path.home() / ".config"
        app_dir = base_dir / "ida-pro-mcp"
    
    return app_dir


def init_files(base_dir: Optional[Union[str, Path]] = None) -> bool:
    """
    Initialize all required files and directories.
    
    Args:
        base_dir: Base directory for file initialization (uses app data dir if None)
        
    Returns:
        bool: True if all files were initialized successfully, False otherwise
    """
    try:
        # Determine base directory
        if base_dir is None:
            base_dir = get_app_data_dir()
        else:
            base_dir = Path(base_dir)
        
        logger.info(f"Initializing files in: {base_dir}")
        
        # Create required directories
        all_dirs_created = True
        for dir_name in REQUIRED_DIRECTORIES:
            dir_path = base_dir / dir_name
            if not ensure_directory_exists(dir_path):
                all_dirs_created = False
        
        # Create template files
        all_files_created = True
        for filename, content in DEFAULT_TEMPLATES.items():
            file_path = base_dir / "templates" / filename
            if not create_template_file(file_path, content):
                all_files_created = False
            
            # Also create in config directory if it doesn't exist
            config_file_path = base_dir / "config" / filename
            if not config_file_path.exists():
                if not create_template_file(config_file_path, content):
                    all_files_created = False
        
        return all_dirs_created and all_files_created
    except Exception as e:
        logger.error(f"Failed to initialize files: {str(e)}")
        return False


def update_file(file_path: Union[str, Path], updates: Dict[str, Any], create_if_missing: bool = True) -> bool:
    """
    Update a JSON file with the provided updates.
    
    Args:
        file_path: Path to the JSON file
        updates: Dictionary of updates to apply
        create_if_missing: Whether to create the file if it doesn't exist
        
    Returns:
        bool: True if file was updated successfully, False otherwise
    """
    try:
        path = Path(file_path)
        
        # Create file with default content if it doesn't exist
        if not path.exists():
            if not create_if_missing:
                logger.warning(f"File does not exist and create_if_missing is False: {path}")
                return False
            
            # Create parent directory if needed
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty JSON file
            with open(path, 'w') as f:
                json.dump({}, f, indent=2)
        
        # Read existing content
        with open(path, 'r') as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError:
                # File exists but is not valid JSON
                content = {}
        
        # Create backup before modifying
        backup_dir = Path(file_path).parent.parent / "backups"
        backup_file(path, backup_dir)
        
        # Update content
        if isinstance(content, dict):
            content.update(updates)
        else:
            # If content is not a dict, replace it entirely
            content = updates
        
        # Write updated content
        with open(path, 'w') as f:
            json.dump(content, f, indent=2)
        
        logger.info(f"Updated file: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to update file {file_path}: {str(e)}")
        return False


def verify_file_integrity(file_path: Union[str, Path], template_name: Optional[str] = None) -> bool:
    """
    Verify that a file exists and has valid content.
    
    Args:
        file_path: Path to the file to verify
        template_name: Name of the template to use if file needs to be recreated
        
    Returns:
        bool: True if file exists and has valid content, False otherwise
    """
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            logger.warning(f"File does not exist: {path}")
            
            # Recreate from template if specified
            if template_name and template_name in DEFAULT_TEMPLATES:
                return create_template_file(path, DEFAULT_TEMPLATES[template_name])
            return False
        
        # Check if file is readable
        if not os.access(path, os.R_OK):
            logger.warning(f"File is not readable: {path}")
            return False
        
        # For JSON files, check if content is valid
        if path.suffix.lower() == '.json':
            try:
                with open(path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"File contains invalid JSON: {path}")
                
                # Recreate from template if specified
                if template_name and template_name in DEFAULT_TEMPLATES:
                    return create_template_file(path, DEFAULT_TEMPLATES[template_name], overwrite=True)
                return False
        
        return True
    except Exception as e:
        logger.error(f"Failed to verify file integrity for {file_path}: {str(e)}")
        return False

