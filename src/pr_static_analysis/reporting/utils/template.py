"""
Template Utilities

This module provides utilities for loading and rendering templates.
"""

import os
import string
from typing import Any, Dict, Optional


def load_template(template_path: str) -> str:
    """
    Load a template file.
    
    Args:
        template_path: Path to the template file
        
    Returns:
        The loaded template as a string
        
    Raises:
        FileNotFoundError: If the template file does not exist
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def render_template(template: str, context: Dict[str, Any]) -> str:
    """
    Render a template with the given context.
    
    Args:
        template: Template string
        context: Context dictionary for template rendering
        
    Returns:
        The rendered template
    """
    # Use string.Template for simple variable substitution
    template = string.Template(template)
    return template.safe_substitute(context)

