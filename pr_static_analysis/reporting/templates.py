"""
Templates module for PR static analysis reporting.

This module provides customizable templates for reports.
"""
import os
import re
import logging
from typing import Dict, Any, Optional
from string import Template

logger = logging.getLogger(__name__)


class ReportTemplate:
    """Base class for report templates."""
    
    def __init__(self, template_str: Optional[str] = None, template_file: Optional[str] = None):
        """Initialize the template.
        
        Args:
            template_str: Template string
            template_file: Path to template file
            
        Raises:
            ValueError: If neither template_str nor template_file is provided
        """
        if template_str:
            self.template = Template(template_str)
        elif template_file and os.path.exists(template_file):
            with open(template_file, 'r') as f:
                self.template = Template(f.read())
        else:
            raise ValueError("Either template_str or template_file must be provided")
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render the template with the given context.
        
        Args:
            context: Template context
            
        Returns:
            Rendered template
        """
        try:
            # Convert any non-string values to strings
            safe_context = {}
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    import json
                    safe_context[key] = json.dumps(value)
                else:
                    safe_context[key] = str(value)
            
            return self.template.safe_substitute(safe_context)
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return f"Error rendering template: {e}"


class MarkdownTemplateProvider:
    """Provider for Markdown templates."""
    
    DEFAULT_TEMPLATE = """# PR Analysis Report for #${pr_number}

**PR:** [${pr_title}](${pr_url})
**Base:** `${pr_base}`
**Head:** `${pr_head}`

## Summary

- **Errors:** ${error_count}
- **Warnings:** ${warning_count}
- **Info:** ${info_count}
- **Total:** ${total_count}

${issues_section}

*Generated at ${timestamp}*
"""
    
    DEFAULT_ISSUES_SECTION = """## Issues

${issues}
"""
    
    DEFAULT_ISSUE_TEMPLATE = """### ${severity_icon} ${rule_id}: ${message}

**File:** `${file}`
**Line:** ${line}

"""
    
    DEFAULT_NO_ISSUES = """No issues found! :white_check_mark:
"""
    
    def __init__(self):
        """Initialize the template provider."""
        self.main_template = ReportTemplate(template_str=self.DEFAULT_TEMPLATE)
        self.issues_section_template = ReportTemplate(template_str=self.DEFAULT_ISSUES_SECTION)
        self.issue_template = ReportTemplate(template_str=self.DEFAULT_ISSUE_TEMPLATE)
        self.no_issues_template = ReportTemplate(template_str=self.DEFAULT_NO_ISSUES)
    
    def render_report(self, report: Dict[str, Any]) -> str:
        """Render a report using the templates.
        
        Args:
            report: The report to render
            
        Returns:
            Rendered report
        """
        # Prepare context for main template
        pr_info = report['pr']
        summary = report['summary']
        
        context = {
            'pr_number': pr_info['number'],
            'pr_title': pr_info['title'],
            'pr_url': pr_info['url'],
            'pr_base': pr_info['base'],
            'pr_head': pr_info['head'],
            'error_count': summary['error_count'],
            'warning_count': summary['warning_count'],
            'info_count': summary['info_count'],
            'total_count': summary['total_count'],
            'timestamp': report['timestamp']
        }
        
        # Render issues section
        if summary['total_count'] > 0:
            issues_text = self._render_issues(report['results'])
            issues_section = self.issues_section_template.render({'issues': issues_text})
        else:
            issues_section = self.no_issues_template.render({})
        
        context['issues_section'] = issues_section
        
        # Render main template
        return self.main_template.render(context)
    
    def _render_issues(self, results: list) -> str:
        """Render issues.
        
        Args:
            results: List of analysis results
            
        Returns:
            Rendered issues
        """
        issues_text = ""
        
        for result in results:
            severity = result.get('severity', 'info')
            severity_icon = self._get_severity_icon(severity)
            
            issue_context = {
                'severity_icon': severity_icon,
                'rule_id': result.get('rule_id', 'unknown'),
                'message': result.get('message', ''),
                'file': result.get('file', ''),
                'line': result.get('line', '')
            }
            
            issues_text += self.issue_template.render(issue_context)
        
        return issues_text
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get an icon for a severity level.
        
        Args:
            severity: The severity level
            
        Returns:
            Icon string for the severity
        """
        if severity == "error":
            return ":x:"
        elif severity == "warning":
            return ":warning:"
        else:
            return ":information_source:"


class HTMLTemplateProvider:
    """Provider for HTML templates."""
    
    DEFAULT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PR Analysis Report #${pr_number}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        h1 { color: #333; }
        h2 { color: #444; margin-top: 20px; }
        h3 { margin-top: 15px; }
        .pr-info { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .summary { display: flex; gap: 20px; margin-bottom: 20px; }
        .summary-item { padding: 10px; border-radius: 5px; text-align: center; flex: 1; }
        .error { background-color: #ffebee; }
        .warning { background-color: #fff8e1; }
        .info { background-color: #e3f2fd; }
        .total { background-color: #f5f5f5; }
        .issue { border-left: 4px solid #ddd; padding-left: 15px; margin-bottom: 20px; }
        .issue.error { border-left-color: #f44336; }
        .issue.warning { border-left-color: #ff9800; }
        .issue.info { border-left-color: #2196f3; }
        .file-info { font-family: monospace; background-color: #f5f5f5; padding: 5px; }
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <h1>PR Analysis Report for #${pr_number}</h1>
    
    <div class="pr-info">
        <p><strong>PR:</strong> <a href="${pr_url}">${pr_title}</a></p>
        <p><strong>Base:</strong> <code>${pr_base}</code></p>
        <p><strong>Head:</strong> <code>${pr_head}</code></p>
    </div>
    
    <h2>Summary</h2>
    <div class="summary">
        <div class="summary-item error">
            <h3>Errors</h3>
            <p>${error_count}</p>
        </div>
        <div class="summary-item warning">
            <h3>Warnings</h3>
            <p>${warning_count}</p>
        </div>
        <div class="summary-item info">
            <h3>Info</h3>
            <p>${info_count}</p>
        </div>
        <div class="summary-item total">
            <h3>Total</h3>
            <p>${total_count}</p>
        </div>
    </div>
    
    ${issues_section}
    
    <div class="footer">
        <p>Generated at ${timestamp}</p>
    </div>
</body>
</html>
"""
    
    DEFAULT_ISSUES_SECTION = """<h2>Issues</h2>
${issues}
"""
    
    DEFAULT_ISSUE_TEMPLATE = """<div class="issue ${severity}">
    <h3>${rule_id}: ${message}</h3>
    <p class="file-info"><strong>File:</strong> ${file}</p>
    <p class="file-info"><strong>Line:</strong> ${line}</p>
</div>
"""
    
    DEFAULT_NO_ISSUES = """<p>No issues found! ✅</p>
"""
    
    def __init__(self):
        """Initialize the template provider."""
        self.main_template = ReportTemplate(template_str=self.DEFAULT_TEMPLATE)
        self.issues_section_template = ReportTemplate(template_str=self.DEFAULT_ISSUES_SECTION)
        self.issue_template = ReportTemplate(template_str=self.DEFAULT_ISSUE_TEMPLATE)
        self.no_issues_template = ReportTemplate(template_str=self.DEFAULT_NO_ISSUES)
    
    def render_report(self, report: Dict[str, Any]) -> str:
        """Render a report using the templates.
        
        Args:
            report: The report to render
            
        Returns:
            Rendered report
        """
        # Prepare context for main template
        pr_info = report['pr']
        summary = report['summary']
        
        context = {
            'pr_number': pr_info['number'],
            'pr_title': pr_info['title'],
            'pr_url': pr_info['url'],
            'pr_base': pr_info['base'],
            'pr_head': pr_info['head'],
            'error_count': summary['error_count'],
            'warning_count': summary['warning_count'],
            'info_count': summary['info_count'],
            'total_count': summary['total_count'],
            'timestamp': report['timestamp']
        }
        
        # Render issues section
        if summary['total_count'] > 0:
            issues_text = self._render_issues(report['results'])
            issues_section = self.issues_section_template.render({'issues': issues_text})
        else:
            issues_section = self.no_issues_template.render({})
        
        context['issues_section'] = issues_section
        
        # Render main template
        return self.main_template.render(context)
    
    def _render_issues(self, results: list) -> str:
        """Render issues.
        
        Args:
            results: List of analysis results
            
        Returns:
            Rendered issues
        """
        issues_text = ""
        
        for result in results:
            severity = result.get('severity', 'info')
            
            issue_context = {
                'severity': severity,
                'rule_id': result.get('rule_id', 'unknown'),
                'message': result.get('message', ''),
                'file': result.get('file', ''),
                'line': result.get('line', '')
            }
            
            issues_text += self.issue_template.render(issue_context)
        
        return issues_text


class TemplateManager:
    """Manager for report templates."""
    
    def __init__(self):
        """Initialize the template manager."""
        self.markdown_provider = MarkdownTemplateProvider()
        self.html_provider = HTMLTemplateProvider()
        self.custom_templates = {}
    
    def register_template(self, name: str, template: ReportTemplate):
        """Register a custom template.
        
        Args:
            name: Template name
            template: Template instance
        """
        self.custom_templates[name] = template
    
    def get_template(self, name: str) -> Optional[ReportTemplate]:
        """Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template instance or None if not found
        """
        return self.custom_templates.get(name)
    
    def render_report(self, report: Dict[str, Any], format_type: str) -> str:
        """Render a report using the appropriate template.
        
        Args:
            report: The report to render
            format_type: Output format type (markdown, html)
            
        Returns:
            Rendered report
        """
        format_type = format_type.lower()
        
        if format_type == 'markdown':
            return self.markdown_provider.render_report(report)
        elif format_type == 'html':
            return self.html_provider.render_report(report)
        else:
            logger.warning(f"Unsupported format type for template rendering: {format_type}")
            return ""

