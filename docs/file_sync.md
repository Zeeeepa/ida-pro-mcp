# File Synchronization Module

The File Synchronization module handles file operations and ensures the application has all required files and directories, creating template files with sensible defaults for first-time users.

## Overview

This module provides functionality to:

1. Create and manage directories
2. Create template files with sensible defaults
3. Handle file permissions appropriately
4. Backup files before modifications
5. Update configuration files
6. Verify file integrity

## Usage

### Initializing Files

To initialize all required files and directories:

```python
from ida_pro_mcp.file_sync import init_files

# Initialize files in the default application data directory
init_files()

# Or specify a custom base directory
init_files("/path/to/custom/directory")
```

You can also use the command-line option:

```bash
ida-pro-mcp --init-files
```

### Directory Management

To create directories if they don't exist:

```python
from ida_pro_mcp.file_sync import ensure_directory_exists

# Create a directory if it doesn't exist
ensure_directory_exists("/path/to/directory")
```

### Template Files

To create template files with default content:

```python
from ida_pro_mcp.file_sync import create_template_file

# Create a template file (won't overwrite if it exists)
create_template_file("/path/to/file.txt", "Default content")

# Create a template file and overwrite if it exists
create_template_file("/path/to/file.txt", "New content", overwrite=True)
```

### File Permissions

To set appropriate file permissions:

```python
from ida_pro_mcp.file_sync import set_file_permissions

# Set appropriate permissions for a file
set_file_permissions("/path/to/file.txt")
```

### File Backups

To create backups of files:

```python
from ida_pro_mcp.file_sync import backup_file

# Backup a file
backup_path = backup_file("/path/to/file.txt", "/path/to/backup/directory")
```

### Updating Configuration Files

To update JSON configuration files:

```python
from ida_pro_mcp.file_sync import update_file

# Update a JSON file
update_file("/path/to/config.json", {"new_key": "new_value"})
```

### Verifying File Integrity

To verify that a file exists and has valid content:

```python
from ida_pro_mcp.file_sync import verify_file_integrity

# Verify file integrity
is_valid = verify_file_integrity("/path/to/file.txt")

# Verify and recreate from template if needed
is_valid = verify_file_integrity("/path/to/settings.json", "settings.json")
```

## Default Templates

The module includes the following default templates:

1. `comments.txt` - A template for user comments
2. `settings.json` - Default application settings
3. `.env` - Template for environment variables

## Required Directories

The module creates the following directory structure:

1. `config` - For configuration files
2. `backups` - For file backups
3. `templates` - For template files
4. `logs` - For log files

