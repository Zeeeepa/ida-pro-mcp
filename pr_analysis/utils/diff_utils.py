"""
Diff utilities for PR static analysis.

This module provides utilities for parsing diffs and extracting changed lines.
"""

import re
from typing import Dict, List, Tuple, Set


def parse_diff(diff_text: str) -> Dict[str, Dict[str, any]]:
    """
    Parse a diff and extract file changes.
    
    Args:
        diff_text: The diff text to parse
        
    Returns:
        A dictionary mapping filenames to file change information
    """
    file_changes = {}
    current_file = None
    current_patch = []
    
    # Regular expressions for parsing diff
    file_header_re = re.compile(r"^diff --git a/(.*) b/(.*)$")
    hunk_header_re = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")
    
    for line in diff_text.splitlines():
        # Check for file header
        file_match = file_header_re.match(line)
        if file_match:
            # Save previous file if any
            if current_file and current_patch:
                if current_file in file_changes:
                    file_changes[current_file]["patch"] = "\n".join(current_patch)
                
            # Start new file
            current_file = file_match.group(1)
            current_patch = [line]
            
            # Initialize file change info
            if current_file not in file_changes:
                file_changes[current_file] = {
                    "filename": current_file,
                    "status": "modified",  # Default status
                    "patch": "",
                    "changed_lines": [],
                }
            continue
            
        # Check for file status
        if line.startswith("new file mode"):
            if current_file and current_file in file_changes:
                file_changes[current_file]["status"] = "added"
            current_patch.append(line)
            continue
            
        if line.startswith("deleted file mode"):
            if current_file and current_file in file_changes:
                file_changes[current_file]["status"] = "removed"
            current_patch.append(line)
            continue
            
        # Add line to current patch
        if current_file:
            current_patch.append(line)
            
    # Save last file if any
    if current_file and current_patch:
        if current_file in file_changes:
            file_changes[current_file]["patch"] = "\n".join(current_patch)
            
    # Extract changed lines for each file
    for filename, change_info in file_changes.items():
        if change_info["patch"]:
            change_info["changed_lines"] = get_changed_lines(change_info["patch"])
            
    return file_changes


def get_changed_lines(patch: str) -> List[int]:
    """
    Extract the line numbers that were changed in a patch.
    
    Args:
        patch: The patch text
        
    Returns:
        A list of line numbers that were changed
    """
    changed_lines = []
    hunk_header_re = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")
    
    current_line = 0
    in_hunk = False
    
    for line in patch.splitlines():
        # Check for hunk header
        hunk_match = hunk_header_re.match(line)
        if hunk_match:
            # Extract line numbers from hunk header
            current_line = int(hunk_match.group(3))
            in_hunk = True
            continue
            
        if not in_hunk:
            continue
            
        # Process lines in hunk
        if line.startswith("+") and not line.startswith("+++"):
            # Added line
            changed_lines.append(current_line)
            current_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            # Removed line - don't increment line number
            pass
        else:
            # Context line
            current_line += 1
            
    return changed_lines


def get_line_ranges(line_numbers: List[int], context_lines: int = 3) -> List[Tuple[int, int]]:
    """
    Convert a list of line numbers to ranges with context.
    
    Args:
        line_numbers: The line numbers
        context_lines: The number of context lines to include
        
    Returns:
        A list of (start_line, end_line) tuples
    """
    if not line_numbers:
        return []
        
    # Sort line numbers
    sorted_lines = sorted(line_numbers)
    
    # Initialize ranges
    ranges = []
    current_range = (max(1, sorted_lines[0] - context_lines), sorted_lines[0] + context_lines)
    
    for line in sorted_lines[1:]:
        # If line is within current range, extend the range
        if line <= current_range[1] + context_lines:
            current_range = (current_range[0], line + context_lines)
        else:
            # Otherwise, start a new range
            ranges.append(current_range)
            current_range = (max(1, line - context_lines), line + context_lines)
            
    # Add the last range
    ranges.append(current_range)
    
    return ranges


def get_common_changed_files(diff1: Dict[str, Dict[str, any]], 
                           diff2: Dict[str, Dict[str, any]]) -> Set[str]:
    """
    Get the set of files that were changed in both diffs.
    
    Args:
        diff1: The first diff
        diff2: The second diff
        
    Returns:
        A set of filenames that were changed in both diffs
    """
    return set(diff1.keys()) & set(diff2.keys())


def get_common_changed_lines(diff1: Dict[str, Dict[str, any]], 
                           diff2: Dict[str, Dict[str, any]]) -> Dict[str, List[int]]:
    """
    Get the lines that were changed in both diffs.
    
    Args:
        diff1: The first diff
        diff2: The second diff
        
    Returns:
        A dictionary mapping filenames to lists of line numbers
    """
    common_files = get_common_changed_files(diff1, diff2)
    common_lines = {}
    
    for filename in common_files:
        lines1 = set(diff1[filename].get("changed_lines", []))
        lines2 = set(diff2[filename].get("changed_lines", []))
        common = lines1 & lines2
        if common:
            common_lines[filename] = sorted(common)
            
    return common_lines

