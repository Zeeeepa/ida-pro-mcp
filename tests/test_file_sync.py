"""
Tests for the File Synchronization module.
"""

import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from ida_pro_mcp.file_sync import (
    ensure_directory_exists,
    create_template_file,
    set_file_permissions,
    backup_file,
    cleanup_old_backups,
    init_files,
    update_file,
    verify_file_integrity,
    DEFAULT_TEMPLATES,
    REQUIRED_DIRECTORIES
)


class TestFileSync(unittest.TestCase):
    """Test cases for the file synchronization module."""

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir) / "ida_pro_mcp_test"
    
    def tearDown(self):
        """Clean up the temporary directory after testing."""
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory_exists(self):
        """Test creating directories."""
        # Test creating a simple directory
        test_dir = self.base_dir / "test_dir"
        self.assertTrue(ensure_directory_exists(test_dir))
        self.assertTrue(test_dir.exists())
        
        # Test creating nested directories
        nested_dir = self.base_dir / "nested" / "dir" / "structure"
        self.assertTrue(ensure_directory_exists(nested_dir))
        self.assertTrue(nested_dir.exists())
    
    def test_create_template_file(self):
        """Test creating template files."""
        # Test creating a file
        test_file = self.base_dir / "test_file.txt"
        content = "Test content"
        self.assertTrue(create_template_file(test_file, content))
        self.assertTrue(test_file.exists())
        
        # Verify content
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), content)
        
        # Test not overwriting existing file
        new_content = "New content"
        self.assertTrue(create_template_file(test_file, new_content, overwrite=False))
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), content)  # Should still have original content
        
        # Test overwriting existing file
        self.assertTrue(create_template_file(test_file, new_content, overwrite=True))
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), new_content)  # Should have new content
    
    def test_set_file_permissions(self):
        """Test setting file permissions."""
        test_file = self.base_dir / "permissions_test.txt"
        
        # Create the file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Set permissions
        self.assertTrue(set_file_permissions(test_file))
        
        # Verify file is readable
        self.assertTrue(os.access(test_file, os.R_OK))
    
    def test_backup_file(self):
        """Test backing up files."""
        # Create a file to backup
        source_file = self.base_dir / "source.txt"
        with open(source_file, 'w') as f:
            f.write("Original content")
        
        # Create backup directory
        backup_dir = self.base_dir / "backups"
        
        # Backup the file
        backup_path = backup_file(source_file, backup_dir)
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            self.assertEqual(f.read(), "Original content")
    
    def test_cleanup_old_backups(self):
        """Test cleaning up old backups."""
        # Create backup directory
        backup_dir = self.base_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create multiple backup files
        for i in range(10):
            backup_file = backup_dir / f"test_{i}.txt"
            with open(backup_file, 'w') as f:
                f.write(f"Backup {i}")
        
        # Clean up old backups
        removed = cleanup_old_backups("test", backup_dir, 5)
        
        # Should have removed 5 backups (10 total - 5 max)
        self.assertEqual(removed, 5)
        
        # Verify only 5 backups remain
        remaining = list(backup_dir.glob("test_*"))
        self.assertEqual(len(remaining), 5)
    
    def test_init_files(self):
        """Test initializing all required files and directories."""
        # Initialize files
        self.assertTrue(init_files(self.base_dir))
        
        # Verify directories were created
        for dir_name in REQUIRED_DIRECTORIES:
            dir_path = self.base_dir / dir_name
            self.assertTrue(dir_path.exists())
        
        # Verify template files were created
        for filename in DEFAULT_TEMPLATES:
            template_path = self.base_dir / "templates" / filename
            self.assertTrue(template_path.exists())
            
            config_path = self.base_dir / "config" / filename
            self.assertTrue(config_path.exists())
    
    def test_update_file(self):
        """Test updating JSON files."""
        # Create a JSON file
        json_file = self.base_dir / "config" / "test.json"
        ensure_directory_exists(json_file.parent)
        with open(json_file, 'w') as f:
            json.dump({"key1": "value1"}, f)
        
        # Update the file
        updates = {"key2": "value2", "key3": {"nested": "value"}}
        self.assertTrue(update_file(json_file, updates))
        
        # Verify updates
        with open(json_file, 'r') as f:
            content = json.load(f)
            self.assertEqual(content["key1"], "value1")
            self.assertEqual(content["key2"], "value2")
            self.assertEqual(content["key3"]["nested"], "value")
    
    def test_verify_file_integrity(self):
        """Test verifying file integrity."""
        # Test non-existent file
        non_existent = self.base_dir / "non_existent.txt"
        self.assertFalse(verify_file_integrity(non_existent))
        
        # Test valid file
        valid_file = self.base_dir / "valid.txt"
        with open(valid_file, 'w') as f:
            f.write("Valid content")
        self.assertTrue(verify_file_integrity(valid_file))
        
        # Test invalid JSON file
        invalid_json = self.base_dir / "invalid.json"
        with open(invalid_json, 'w') as f:
            f.write("Not valid JSON")
        self.assertFalse(verify_file_integrity(invalid_json))
        
        # Test recreating from template
        template_file = self.base_dir / "template.json"
        self.assertTrue(verify_file_integrity(template_file, "settings.json"))
        self.assertTrue(template_file.exists())
        with open(template_file, 'r') as f:
            content = json.load(f)
            self.assertTrue("autoSave" in content)


if __name__ == "__main__":
    unittest.main()

