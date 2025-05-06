"""
Visualization components for the PR static analysis system.

This module contains functions for creating visualizations of analysis results,
including charts, graphs, and code highlighting.
"""

import base64
import io
from typing import Dict, List, Optional, Tuple, Any, Union
import html
import re
from collections import Counter

# Try to import visualization libraries, but provide fallbacks if not available
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import networkx as nx
    HAS_VISUALIZATION_LIBS = True
except ImportError:
    HAS_VISUALIZATION_LIBS = False

from .report_generator import ReportResult


def create_severity_chart(results: List[ReportResult]) -> Optional[str]:
    """
    Create a chart showing results by severity.
    
    Args:
        results: A list of ReportResult objects.
        
    Returns:
        A base64-encoded image string, or None if visualization libraries are not available.
    """
    if not HAS_VISUALIZATION_LIBS:
        return _get_visualization_fallback("Severity Chart", results)
    
    # Count results by severity
    severity_counts = Counter(result.severity for result in results)
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define colors for different severities
    colors = {
        'critical': '#d9534f',
        'error': '#f0ad4e',
        'warning': '#5bc0de',
        'info': '#5cb85c',
    }
    
    # Get colors for each severity in the data
    chart_colors = [colors.get(severity, '#777777') for severity in severity_counts.keys()]
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        severity_counts.values(),
        labels=severity_counts.keys(),
        autopct='%1.1f%%',
        startangle=90,
        colors=chart_colors
    )
    
    # Style the chart
    for text in texts:
        text.set_fontsize(12)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')
    
    ax.set_title('Issues by Severity', fontsize=14)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    # Convert plot to base64 image
    return _fig_to_base64(fig)


def create_category_chart(results: List[ReportResult]) -> Optional[str]:
    """
    Create a chart showing results by category.
    
    Args:
        results: A list of ReportResult objects.
        
    Returns:
        A base64-encoded image string, or None if visualization libraries are not available.
    """
    if not HAS_VISUALIZATION_LIBS:
        return _get_visualization_fallback("Category Chart", results)
    
    # Count results by category
    category_counts = Counter(result.category for result in results)
    
    # Sort categories by count (descending)
    categories = [category for category, _ in category_counts.most_common()]
    counts = [category_counts[category] for category in categories]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create horizontal bar chart
    bars = ax.barh(categories, counts, color='#5bc0de')
    
    # Add count labels to the right of each bar
    for i, bar in enumerate(bars):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height()/2,
            str(counts[i]),
            va='center'
        )
    
    # Style the chart
    ax.set_title('Issues by Category', fontsize=14)
    ax.set_xlabel('Number of Issues', fontsize=12)
    ax.set_ylabel('Category', fontsize=12)
    ax.tick_params(axis='y', labelsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert plot to base64 image
    return _fig_to_base64(fig)


def create_file_chart(results: List[ReportResult]) -> Optional[str]:
    """
    Create a chart showing results by file.
    
    Args:
        results: A list of ReportResult objects.
        
    Returns:
        A base64-encoded image string, or None if visualization libraries are not available.
    """
    if not HAS_VISUALIZATION_LIBS:
        return _get_visualization_fallback("File Chart", results)
    
    # Filter results with file_path
    file_results = [result for result in results if result.file_path]
    
    # Count results by file
    file_counts = Counter(result.file_path for result in file_results)
    
    # Get top 10 files by issue count
    top_files = [file for file, _ in file_counts.most_common(10)]
    counts = [file_counts[file] for file in top_files]
    
    # Shorten file paths for display
    display_files = [_shorten_path(file) for file in top_files]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create horizontal bar chart
    bars = ax.barh(display_files, counts, color='#5cb85c')
    
    # Add count labels to the right of each bar
    for i, bar in enumerate(bars):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height()/2,
            str(counts[i]),
            va='center'
        )
    
    # Style the chart
    ax.set_title('Top 10 Files by Issue Count', fontsize=14)
    ax.set_xlabel('Number of Issues', fontsize=12)
    ax.set_ylabel('File', fontsize=12)
    ax.tick_params(axis='y', labelsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert plot to base64 image
    return _fig_to_base64(fig)


def create_dependency_graph(results: List[ReportResult]) -> Optional[str]:
    """
    Create a graph showing dependencies.
    
    Args:
        results: A list of ReportResult objects.
        
    Returns:
        A base64-encoded image string, or None if visualization libraries are not available.
    """
    if not HAS_VISUALIZATION_LIBS:
        return _get_visualization_fallback("Dependency Graph", results)
    
    # This is a placeholder implementation
    # In a real implementation, this would extract dependency information from results
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Extract files with issues
    files = set(result.file_path for result in results if result.file_path)
    
    # Add nodes for each file
    for file in files:
        G.add_node(_shorten_path(file))
    
    # Add some example edges (in a real implementation, these would be based on actual dependencies)
    # This is just for demonstration purposes
    nodes = list(G.nodes())
    if len(nodes) > 1:
        G.add_edge(nodes[0], nodes[1])
    if len(nodes) > 2:
        G.add_edge(nodes[0], nodes[2])
    if len(nodes) > 3:
        G.add_edge(nodes[1], nodes[3])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw the graph
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color='#5bc0de', node_size=500, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color='#777777', width=1.5, alpha=0.7, arrows=True)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    # Style the chart
    ax.set_title('File Dependency Graph', fontsize=14)
    ax.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert plot to base64 image
    return _fig_to_base64(fig)


def create_call_graph(results: List[ReportResult]) -> Optional[str]:
    """
    Create a graph showing function calls.
    
    Args:
        results: A list of ReportResult objects.
        
    Returns:
        A base64-encoded image string, or None if visualization libraries are not available.
    """
    if not HAS_VISUALIZATION_LIBS:
        return _get_visualization_fallback("Call Graph", results)
    
    # This is a placeholder implementation
    # In a real implementation, this would extract call information from results
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add some example nodes and edges (in a real implementation, these would be based on actual function calls)
    # This is just for demonstration purposes
    G.add_node("main()")
    G.add_node("process_data()")
    G.add_node("validate_input()")
    G.add_node("format_output()")
    G.add_node("save_results()")
    
    G.add_edge("main()", "process_data()")
    G.add_edge("main()", "save_results()")
    G.add_edge("process_data()", "validate_input()")
    G.add_edge("process_data()", "format_output()")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw the graph
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color='#f0ad4e', node_size=700, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color='#777777', width=1.5, alpha=0.7, arrows=True)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    # Style the chart
    ax.set_title('Function Call Graph', fontsize=14)
    ax.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert plot to base64 image
    return _fig_to_base64(fig)


def create_inheritance_graph(results: List[ReportResult]) -> Optional[str]:
    """
    Create a graph showing class inheritance.
    
    Args:
        results: A list of ReportResult objects.
        
    Returns:
        A base64-encoded image string, or None if visualization libraries are not available.
    """
    if not HAS_VISUALIZATION_LIBS:
        return _get_visualization_fallback("Inheritance Graph", results)
    
    # This is a placeholder implementation
    # In a real implementation, this would extract inheritance information from results
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add some example nodes and edges (in a real implementation, these would be based on actual class inheritance)
    # This is just for demonstration purposes
    G.add_node("BaseClass")
    G.add_node("ChildClass1")
    G.add_node("ChildClass2")
    G.add_node("GrandchildClass1")
    G.add_node("GrandchildClass2")
    
    G.add_edge("BaseClass", "ChildClass1")
    G.add_edge("BaseClass", "ChildClass2")
    G.add_edge("ChildClass1", "GrandchildClass1")
    G.add_edge("ChildClass2", "GrandchildClass2")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw the graph
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if hasattr(nx, 'nx_agraph') else nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color='#d9534f', node_size=700, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color='#777777', width=1.5, alpha=0.7, arrows=True)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    # Style the chart
    ax.set_title('Class Inheritance Graph', fontsize=14)
    ax.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert plot to base64 image
    return _fig_to_base64(fig)


def highlight_code(code: str, language: str = "python") -> str:
    """
    Highlight code syntax.
    
    Args:
        code: The code to highlight.
        language: The programming language of the code.
        
    Returns:
        HTML string with highlighted code.
    """
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        
        lexer = get_lexer_by_name(language, stripall=True)
        formatter = HtmlFormatter(linenos=True, cssclass="source")
        result = highlight(code, lexer, formatter)
        
        # Add CSS
        css = HtmlFormatter().get_style_defs('.source')
        result = f"<style>{css}</style>{result}"
        
        return result
    except ImportError:
        # Fallback if pygments is not available
        return f"<pre><code class='{language}'>{html.escape(code)}</code></pre>"


def highlight_diff(diff: str) -> str:
    """
    Highlight diff syntax.
    
    Args:
        diff: The diff to highlight.
        
    Returns:
        HTML string with highlighted diff.
    """
    try:
        from pygments import highlight
        from pygments.lexers import DiffLexer
        from pygments.formatters import HtmlFormatter
        
        formatter = HtmlFormatter(linenos=True, cssclass="source")
        result = highlight(diff, DiffLexer(), formatter)
        
        # Add CSS
        css = HtmlFormatter().get_style_defs('.source')
        result = f"<style>{css}</style>{result}"
        
        return result
    except ImportError:
        # Fallback if pygments is not available
        html_diff = ""
        for line in diff.split('\n'):
            if line.startswith('+'):
                html_diff += f"<div class='diff-add'>{html.escape(line)}</div>"
            elif line.startswith('-'):
                html_diff += f"<div class='diff-remove'>{html.escape(line)}</div>"
            else:
                html_diff += f"<div class='diff-context'>{html.escape(line)}</div>"
        
        # Add CSS
        css = """
        <style>
            .diff-add { color: green; background-color: #e6ffed; }
            .diff-remove { color: red; background-color: #ffeef0; }
            .diff-context { color: #333; }
        </style>
        """
        
        return f"{css}<pre>{html_diff}</pre>"


def highlight_issues(code: str, issues: List[Dict[str, Any]]) -> str:
    """
    Highlight issues in code.
    
    Args:
        code: The code to highlight.
        issues: A list of issues, each with 'line', 'column', 'message', and 'severity'.
        
    Returns:
        HTML string with highlighted code and issues.
    """
    # First, highlight the code
    highlighted_code = highlight_code(code)
    
    # Then, add issue markers
    # This is a simplified implementation that assumes the highlighted code has line numbers
    
    # Group issues by line
    issues_by_line = {}
    for issue in issues:
        line = issue.get('line', 0)
        if line not in issues_by_line:
            issues_by_line[line] = []
        issues_by_line[line].append(issue)
    
    # Add issue markers to each line
    lines = highlighted_code.split('\n')
    for i, line in enumerate(lines):
        # Check if this is a code line with a line number
        if 'class="lineno"' in line:
            # Extract line number
            match = re.search(r'<span class="lineno">(\s*)(\d+)(\s*)</span>', line)
            if match:
                line_number = int(match.group(2))
                
                # Check if there are issues for this line
                if line_number in issues_by_line:
                    # Add issue markers
                    issue_markers = ""
                    for issue in issues_by_line[line_number]:
                        severity = issue.get('severity', 'info').lower()
                        message = issue.get('message', '')
                        
                        # Create a marker with appropriate color
                        color = {
                            'critical': '#d9534f',
                            'error': '#f0ad4e',
                            'warning': '#5bc0de',
                            'info': '#5cb85c',
                        }.get(severity, '#777777')
                        
                        issue_markers += f'<span class="issue-marker" style="background-color: {color};" title="{html.escape(message)}">⚠</span>'
                    
                    # Add markers to the line
                    line = line.replace('</span>', f'</span>{issue_markers}', 1)
                    lines[i] = line
    
    # Add CSS for issue markers
    css = """
    <style>
        .issue-marker {
            display: inline-block;
            margin-left: 5px;
            padding: 0 5px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            cursor: help;
        }
    </style>
    """
    
    # Combine everything
    result = '\n'.join(lines)
    if '<style>' in result:
        # Add to existing style tag
        result = result.replace('<style>', '<style>\n' + css.replace('<style>', '').replace('</style>', ''))
    else:
        # Add new style tag
        result = css + result
    
    return result


def _fig_to_base64(fig) -> str:
    """
    Convert a matplotlib figure to a base64-encoded string.
    
    Args:
        fig: A matplotlib figure.
        
    Returns:
        A base64-encoded string of the figure.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"


def _shorten_path(path: str, max_length: int = 30) -> str:
    """
    Shorten a file path for display.
    
    Args:
        path: The file path to shorten.
        max_length: The maximum length of the shortened path.
        
    Returns:
        A shortened file path.
    """
    if len(path) <= max_length:
        return path
    
    # Split path into components
    components = path.split('/')
    
    # If there's only one component, truncate it
    if len(components) == 1:
        return components[0][:max_length-3] + '...'
    
    # Keep the first and last components, and replace middle components with '...'
    first = components[0]
    last = components[-1]
    
    # Calculate how much space we have for first and last
    available_space = max_length - 5  # 5 characters for '/.../'
    
    # Allocate space proportionally
    if len(first) + len(last) <= available_space:
        return f"{first}/.../{last}"
    
    # Allocate half the space to each
    half_space = available_space // 2
    
    if len(first) <= half_space and len(last) > half_space:
        # First component fits, truncate last
        return f"{first}/.../{last[:available_space-len(first)-1]}..."
    elif len(first) > half_space and len(last) <= half_space:
        # Last component fits, truncate first
        return f"{first[:available_space-len(last)-1]}.../.../.../{last}"
    else:
        # Truncate both
        return f"{first[:half_space-1]}.../.../.../{last[:half_space-1]}..."


def _get_visualization_fallback(chart_type: str, results: List[ReportResult]) -> str:
    """
    Get a fallback HTML representation when visualization libraries are not available.
    
    Args:
        chart_type: The type of chart.
        results: A list of ReportResult objects.
        
    Returns:
        An HTML string with a fallback representation.
    """
    html_output = f"<div class='visualization-fallback'><h3>{chart_type}</h3>"
    html_output += "<p>Visualization libraries are not available. Here's a text summary:</p>"
    
    if chart_type == "Severity Chart":
        # Count results by severity
        severity_counts = Counter(result.severity for result in results)
        html_output += "<ul>"
        for severity, count in severity_counts.items():
            html_output += f"<li><strong>{severity.capitalize()}:</strong> {count}</li>"
        html_output += "</ul>"
    
    elif chart_type == "Category Chart":
        # Count results by category
        category_counts = Counter(result.category for result in results)
        html_output += "<ul>"
        for category, count in category_counts.most_common():
            html_output += f"<li><strong>{category}:</strong> {count}</li>"
        html_output += "</ul>"
    
    elif chart_type == "File Chart":
        # Count results by file
        file_results = [result for result in results if result.file_path]
        file_counts = Counter(result.file_path for result in file_results)
        html_output += "<ul>"
        for file, count in file_counts.most_common(10):
            html_output += f"<li><strong>{file}:</strong> {count}</li>"
        html_output += "</ul>"
    
    else:
        html_output += f"<p>No text summary available for {chart_type}.</p>"
    
    html_output += "</div>"
    
    return html_output

