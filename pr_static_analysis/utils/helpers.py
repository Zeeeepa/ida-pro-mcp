"""
Helpers Module

This module provides utility functions for the PR static analysis system.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import os
import re
import logging
import json
import yaml
from datetime import datetime

from ..core.analysis_context import AnalysisResult

logger = logging.getLogger(__name__)

def format_results(results: List[AnalysisResult], format_type: str = "text") -> str:
    """
    Format analysis results as a string.
    
    Args:
        results: The analysis results to format.
        format_type: The output format ("text", "json", or "yaml").
        
    Returns:
        A formatted string representation of the results.
    """
    if format_type == "json":
        return format_results_json(results)
    elif format_type == "yaml":
        return format_results_yaml(results)
    else:
        return format_results_text(results)
        
def format_results_json(results: List[AnalysisResult]) -> str:
    """
    Format analysis results as JSON.
    
    Args:
        results: The analysis results to format.
        
    Returns:
        A JSON string representation of the results.
    """
    result_dicts = []
    
    for result in results:
        result_dict = {
            "rule_id": result.rule_id,
            "status": result.status,
            "message": result.message,
            "created_at": result.created_at.isoformat(),
        }
        
        if result.file_path:
            result_dict["file_path"] = result.file_path
            
        if result.line_number is not None:
            result_dict["line_number"] = result.line_number
            
        if result.details:
            result_dict["details"] = result.details
            
        result_dicts.append(result_dict)
        
    return json.dumps(result_dicts, indent=2)
    
def format_results_yaml(results: List[AnalysisResult]) -> str:
    """
    Format analysis results as YAML.
    
    Args:
        results: The analysis results to format.
        
    Returns:
        A YAML string representation of the results.
    """
    result_dicts = []
    
    for result in results:
        result_dict = {
            "rule_id": result.rule_id,
            "status": result.status,
            "message": result.message,
            "created_at": result.created_at.isoformat(),
        }
        
        if result.file_path:
            result_dict["file_path"] = result.file_path
            
        if result.line_number is not None:
            result_dict["line_number"] = result.line_number
            
        if result.details:
            result_dict["details"] = result.details
            
        result_dicts.append(result_dict)
        
    return yaml.dump(result_dicts, sort_keys=False)
    
def format_results_text(results: List[AnalysisResult]) -> str:
    """
    Format analysis results as plain text.
    
    Args:
        results: The analysis results to format.
        
    Returns:
        A text string representation of the results.
    """
    if not results:
        return "No results."
        
    lines = []
    
    # Group results by status
    results_by_status = {}
    for result in results:
        if result.status not in results_by_status:
            results_by_status[result.status] = []
        results_by_status[result.status].append(result)
        
    # Count results by status
    status_counts = {status: len(results) for status, results in results_by_status.items()}
    
    # Add summary
    lines.append("Analysis Results Summary:")
    for status, count in status_counts.items():
        lines.append(f"  {status.upper()}: {count}")
    lines.append("")
    
    # Add detailed results
    for status in ["error", "fail", "warning", "pass"]:
        if status in results_by_status:
            lines.append(f"{status.upper()} Results:")
            for result in results_by_status[status]:
                location = ""
                if result.file_path:
                    location = f"{result.file_path}"
                    if result.line_number is not None:
                        location += f":{result.line_number}"
                        
                lines.append(f"  [{result.rule_id}] {result.message}")
                if location:
                    lines.append(f"    Location: {location}")
                    
                if result.details:
                    lines.append(f"    Details: {json.dumps(result.details)}")
                    
                lines.append("")
                
    return "\n".join(lines)
    
def save_results_to_file(results: List[AnalysisResult], file_path: str, format_type: str = "text") -> None:
    """
    Save analysis results to a file.
    
    Args:
        results: The analysis results to save.
        file_path: The path to the output file.
        format_type: The output format ("text", "json", or "yaml").
    """
    formatted_results = format_results(results, format_type)
    
    with open(file_path, "w") as f:
        f.write(formatted_results)
        
    logger.info(f"Saved analysis results to {file_path}")
    
def find_files_by_extension(directory: str, extensions: Set[str]) -> List[str]:
    """
    Find files with specific extensions in a directory (recursively).
    
    Args:
        directory: The directory to search.
        extensions: Set of file extensions to look for (e.g., {".py", ".js"}).
        
    Returns:
        A list of file paths.
    """
    result = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in extensions:
                result.append(os.path.join(root, file))
                
    return result
    
def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
    """
    Find files matching a regex pattern in a directory (recursively).
    
    Args:
        directory: The directory to search.
        pattern: Regex pattern to match against file paths.
        
    Returns:
        A list of file paths.
    """
    result = []
    regex = re.compile(pattern)
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.search(file_path):
                result.append(file_path)
                
    return result
    
def get_file_diff(file_path: str, base_dir: str, head_dir: str) -> Optional[str]:
    """
    Get the diff for a file between base and head directories.
    
    Args:
        file_path: The path to the file, relative to the repository root.
        base_dir: The base directory (old version).
        head_dir: The head directory (new version).
        
    Returns:
        The diff as a string, or None if the file doesn't exist in either directory.
    """
    base_file = os.path.join(base_dir, file_path)
    head_file = os.path.join(head_dir, file_path)
    
    if not os.path.exists(base_file) and not os.path.exists(head_file):
        return None
        
    if not os.path.exists(base_file):
        with open(head_file, "r") as f:
            head_content = f.read()
        return f"--- /dev/null\n+++ {file_path}\n@@ -0,0 +1,{len(head_content.splitlines())} @@\n" + "".join(f"+{line}\n" for line in head_content.splitlines())
        
    if not os.path.exists(head_file):
        with open(base_file, "r") as f:
            base_content = f.read()
        return f"--- {file_path}\n+++ /dev/null\n@@ -1,{len(base_content.splitlines())} +0,0 @@\n" + "".join(f"-{line}\n" for line in base_content.splitlines())
        
    import difflib
    
    with open(base_file, "r") as f:
        base_content = f.readlines()
        
    with open(head_file, "r") as f:
        head_content = f.readlines()
        
    diff = difflib.unified_diff(
        base_content, head_content,
        fromfile=file_path, tofile=file_path
    )
    
    return "".join(diff)

