"""
HTML Formatter Module

This module provides a formatter for converting analysis results into HTML format.
"""

from typing import Any, Dict, Optional, List
import html

from .base_formatter import BaseFormatter


class HTMLFormatter(BaseFormatter):
    """
    Formatter for converting analysis results into HTML format.
    
    This formatter generates an HTML report from analysis results.
    It supports customization of the report structure, content, and styling.
    """
    
    def __init__(
        self,
        include_summary: bool = True,
        include_details: bool = True,
        include_issues: bool = True,
        include_files: bool = True,
        include_metrics: bool = True,
        custom_sections: Optional[Dict[str, Any]] = None,
        css_styles: Optional[str] = None,
        use_bootstrap: bool = False
    ):
        """
        Initialize a new HTMLFormatter.
        
        Args:
            include_summary: Whether to include a summary section
            include_details: Whether to include a details section
            include_issues: Whether to include an issues section
            include_files: Whether to include a files section
            include_metrics: Whether to include a metrics section
            custom_sections: Optional dictionary of custom sections to include
            css_styles: Optional custom CSS styles to include
            use_bootstrap: Whether to include Bootstrap CSS
        """
        self.include_summary = include_summary
        self.include_details = include_details
        self.include_issues = include_issues
        self.include_files = include_files
        self.include_metrics = include_metrics
        self.custom_sections = custom_sections or {}
        self.css_styles = css_styles
        self.use_bootstrap = use_bootstrap
        
    def format(
        self, 
        analysis_results: Dict[str, Any], 
        visualizations: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Format analysis results into an HTML report.
        
        Args:
            analysis_results: Analysis results to format
            visualizations: Optional dictionary of visualization data
            **kwargs: Additional formatter-specific arguments
            
        Returns:
            The formatted report as an HTML string
        """
        # Start building the HTML document
        html_parts = []
        
        # Add HTML header
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang=\"en\">")
        html_parts.append("<head>")
        html_parts.append("    <meta charset=\"UTF-8\">")
        html_parts.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        
        # Add title
        title = kwargs.get('title', 'PR Static Analysis Report')
        html_parts.append(f"    <title>{html.escape(title)}</title>")
        
        # Add Bootstrap if requested
        if self.use_bootstrap:
            html_parts.append("    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\">")
        
        # Add custom CSS styles
        html_parts.append("    <style>")
        if self.css_styles:
            html_parts.append(self.css_styles)
        else:
            # Default styles
            html_parts.append("""
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1, h2, h3, h4 {
            color: #2c3e50;
        }
        h1 {
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            margin-top: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .issue {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 4px;
        }
        .issue-error {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
        }
        .issue-warning {
            background-color: #fff8e1;
            border-left: 4px solid #ffc107;
        }
        .issue-info {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .file-list {
            list-style-type: none;
            padding-left: 0;
        }
        .file-item {
            padding: 5px 0;
            font-family: monospace;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .metrics-table th, .metrics-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .metrics-table th {
            background-color: #f2f2f2;
        }
        .visualization {
            margin: 20px 0;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: monospace;
        }
        """)
        html_parts.append("    </style>")
        html_parts.append("</head>")
        
        # Start body
        if self.use_bootstrap:
            html_parts.append("<body>")
            html_parts.append("    <div class=\"container\">")
        else:
            html_parts.append("<body>")
            html_parts.append("    <div class=\"container\">")
        
        # Add title
        html_parts.append(f"        <h1>{html.escape(title)}</h1>")
        
        # Add summary section
        if self.include_summary and 'summary' in analysis_results:
            html_parts.append("        <h2>Summary</h2>")
            html_parts.append(f"        <p>{html.escape(analysis_results['summary'])}</p>")
        
        # Add issues section
        if self.include_issues and 'issues' in analysis_results:
            html_parts.append("        <h2>Issues</h2>")
            
            issues = analysis_results['issues']
            if not issues:
                html_parts.append("        <p>No issues found.</p>")
            else:
                html_parts.append("        <div class=\"issues\">")
                for issue in issues:
                    severity = issue.get('severity', 'info').lower()
                    message = issue.get('message', '')
                    file = issue.get('file', '')
                    line = issue.get('line', '')
                    
                    location = ""
                    if file:
                        location = f" in <code>{html.escape(file)}</code>"
                        if line:
                            location += f" at line {line}"
                    
                    html_parts.append(f"            <div class=\"issue issue-{severity}\">")
                    html_parts.append(f"                <strong>[{severity.upper()}]</strong>{location}: {html.escape(message)}")
                    html_parts.append("            </div>")
                html_parts.append("        </div>")
        
        # Add files section
        if self.include_files and any(k in analysis_results for k in ['files_added', 'files_modified', 'files_removed']):
            html_parts.append("        <h2>Files</h2>")
            
            files_added = analysis_results.get('files_added', [])
            files_modified = analysis_results.get('files_modified', [])
            files_removed = analysis_results.get('files_removed', [])
            
            if files_added:
                html_parts.append("        <h3>Files Added</h3>")
                html_parts.append("        <ul class=\"file-list\">")
                for file in sorted(files_added):
                    html_parts.append(f"            <li class=\"file-item\"><code>{html.escape(file)}</code></li>")
                html_parts.append("        </ul>")
            
            if files_modified:
                html_parts.append("        <h3>Files Modified</h3>")
                html_parts.append("        <ul class=\"file-list\">")
                for file in sorted(files_modified):
                    html_parts.append(f"            <li class=\"file-item\"><code>{html.escape(file)}</code></li>")
                html_parts.append("        </ul>")
            
            if files_removed:
                html_parts.append("        <h3>Files Removed</h3>")
                html_parts.append("        <ul class=\"file-list\">")
                for file in sorted(files_removed):
                    html_parts.append(f"            <li class=\"file-item\"><code>{html.escape(file)}</code></li>")
                html_parts.append("        </ul>")
        
        # Add metrics section
        if self.include_metrics and 'metrics' in analysis_results:
            html_parts.append("        <h2>Metrics</h2>")
            
            metrics = analysis_results['metrics']
            html_parts.append("        <table class=\"metrics-table\">")
            html_parts.append("            <tr><th>Metric</th><th>Value</th></tr>")
            for key, value in metrics.items():
                # Format the key for better readability
                formatted_key = key.replace('_', ' ').title()
                html_parts.append(f"            <tr><td>{html.escape(formatted_key)}</td><td>{html.escape(str(value))}</td></tr>")
            html_parts.append("        </table>")
        
        # Add visualizations
        if visualizations:
            html_parts.append("        <h2>Visualizations</h2>")
            
            for viz_name, viz_data in visualizations.items():
                formatted_name = viz_name.replace('_', ' ').title()
                html_parts.append(f"        <h3>{html.escape(formatted_name)}</h3>")
                html_parts.append("        <div class=\"visualization\">")
                
                if isinstance(viz_data, str):
                    # If the visualization is HTML content, add it directly
                    html_parts.append(f"            {viz_data}")
                elif isinstance(viz_data, dict) and 'html' in viz_data:
                    # If the visualization has an 'html' key, use that
                    html_parts.append(f"            {viz_data['html']}")
                else:
                    # Otherwise, convert to string and escape
                    html_parts.append(f"            <pre>{html.escape(str(viz_data))}</pre>")
                
                html_parts.append("        </div>")
        
        # Add custom sections
        for section_name, section_content in self.custom_sections.items():
            html_parts.append(f"        <h2>{html.escape(section_name)}</h2>")
            
            if callable(section_content):
                # If the section content is a function, call it with the analysis results
                content = section_content(analysis_results)
                html_parts.append(f"        <div>{content}</div>")
            else:
                # Otherwise, add the content directly
                html_parts.append(f"        <div>{str(section_content)}</div>")
        
        # Add details section
        if self.include_details and 'details' in analysis_results:
            html_parts.append("        <h2>Details</h2>")
            
            details = analysis_results['details']
            if isinstance(details, str):
                html_parts.append(f"        <div>{html.escape(details)}</div>")
            elif isinstance(details, dict):
                for key, value in details.items():
                    html_parts.append(f"        <h3>{html.escape(key)}</h3>")
                    html_parts.append(f"        <div>{html.escape(str(value))}</div>")
            elif isinstance(details, list):
                for item in details:
                    if isinstance(item, dict) and 'title' in item and 'content' in item:
                        html_parts.append(f"        <h3>{html.escape(item['title'])}</h3>")
                        html_parts.append(f"        <div>{html.escape(item['content'])}</div>")
                    else:
                        html_parts.append(f"        <div>{html.escape(str(item))}</div>")
        
        # Close body and HTML
        html_parts.append("    </div>")
        
        # Add Bootstrap JS if requested
        if self.use_bootstrap:
            html_parts.append("    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>")
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)

