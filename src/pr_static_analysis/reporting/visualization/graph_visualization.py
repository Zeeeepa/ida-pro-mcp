"""
Graph Visualization Module

This module provides a visualization for generating graphs from analysis results.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from .base_visualization import BaseVisualization

try:
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import io
    import base64
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


class GraphVisualization(BaseVisualization):
    """
    Visualization for generating graphs from analysis results.
    
    This visualization can generate various types of graphs (directed, undirected, etc.)
    from analysis results using networkx and matplotlib.
    """
    
    def __init__(
        self,
        graph_type: str = 'directed',
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 8),
        dpi: int = 100,
        format: str = 'png',
        layout: str = 'spring'
    ):
        """
        Initialize a new GraphVisualization.
        
        Args:
            graph_type: Type of graph to generate ('directed', 'undirected', 'multi', etc.)
            title: Graph title
            figsize: Figure size (width, height) in inches
            dpi: Figure resolution in dots per inch
            format: Image format ('png', 'jpg', 'svg', etc.)
            layout: Graph layout algorithm ('spring', 'circular', 'random', 'shell', etc.)
            
        Raises:
            ImportError: If networkx or matplotlib is not installed
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "Networkx and matplotlib are required for GraphVisualization. "
                "Install them with: pip install networkx matplotlib"
            )
        
        self.graph_type = graph_type
        self.title = title
        self.figsize = figsize
        self.dpi = dpi
        self.format = format
        self.layout = layout
        
    def generate(
        self, 
        analysis_results: Dict[str, Any], 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a graph visualization from analysis results.
        
        Args:
            analysis_results: Analysis results to visualize
            **kwargs: Additional visualization-specific arguments, including:
                - nodes: List of nodes to include in the graph
                - edges: List of edges to include in the graph
                - node_attrs: Dictionary of node attributes
                - edge_attrs: Dictionary of edge attributes
                - graph_type: Override the default graph type
                - title: Override the default graph title
                - figsize: Override the default figure size
                - dpi: Override the default figure resolution
                - format: Override the default image format
                - layout: Override the default layout algorithm
                - as_html: Whether to return the graph as an HTML img tag
                - as_base64: Whether to return the graph as a base64-encoded string
                - save_path: Path to save the graph to
            
        Returns:
            A dictionary containing the visualization data, including:
                - image: The graph image as a base64-encoded string
                - html: The graph as an HTML img tag (if as_html is True)
                - format: The image format
                - graph_type: The graph type
                - title: The graph title
        """
        try:
            # Get graph parameters
            nodes = kwargs.get('nodes')
            edges = kwargs.get('edges')
            node_attrs = kwargs.get('node_attrs', {})
            edge_attrs = kwargs.get('edge_attrs', {})
            graph_type = kwargs.get('graph_type', self.graph_type)
            title = kwargs.get('title', self.title)
            figsize = kwargs.get('figsize', self.figsize)
            dpi = kwargs.get('dpi', self.dpi)
            format = kwargs.get('format', self.format)
            layout = kwargs.get('layout', self.layout)
            as_html = kwargs.get('as_html', True)
            as_base64 = kwargs.get('as_base64', True)
            save_path = kwargs.get('save_path')
            
            # Extract nodes and edges if not provided
            if not nodes or not edges:
                extracted_data = self._extract_graph_data(analysis_results)
                nodes = nodes or extracted_data.get('nodes', [])
                edges = edges or extracted_data.get('edges', [])
            
            if not nodes or not edges:
                logging.warning("No graph data to visualize")
                return {
                    'error': "No graph data to visualize",
                    'graph_type': graph_type,
                    'title': title
                }
            
            # Create the graph based on the graph type
            if graph_type == 'directed':
                G = nx.DiGraph()
            elif graph_type == 'undirected':
                G = nx.Graph()
            elif graph_type == 'multi':
                G = nx.MultiGraph()
            elif graph_type == 'directed_multi':
                G = nx.MultiDiGraph()
            else:
                logging.warning(f"Unsupported graph type: {graph_type}")
                return {
                    'error': f"Unsupported graph type: {graph_type}",
                    'graph_type': graph_type,
                    'title': title
                }
            
            # Add nodes and edges to the graph
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
            
            # Add node and edge attributes
            for node, attrs in node_attrs.items():
                for key, value in attrs.items():
                    G.nodes[node][key] = value
            
            for edge, attrs in edge_attrs.items():
                for key, value in attrs.items():
                    G.edges[edge][key] = value
            
            # Create the figure
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            
            # Set the layout
            if layout == 'spring':
                pos = nx.spring_layout(G)
            elif layout == 'circular':
                pos = nx.circular_layout(G)
            elif layout == 'random':
                pos = nx.random_layout(G)
            elif layout == 'shell':
                pos = nx.shell_layout(G)
            elif layout == 'spectral':
                pos = nx.spectral_layout(G)
            else:
                pos = nx.spring_layout(G)
            
            # Draw the graph
            nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, 
                    edge_color='black', linewidths=1, font_size=10, ax=ax)
            
            # Set the title
            if title:
                ax.set_title(title)
            
            # Save the graph to a file if requested
            if save_path:
                plt.savefig(save_path, format=format, dpi=dpi)
            
            # Convert the graph to a base64-encoded string
            if as_base64 or as_html:
                buf = io.BytesIO()
                plt.savefig(buf, format=format, dpi=dpi)
                buf.seek(0)
                img_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
                
                result = {
                    'image': img_data,
                    'format': format,
                    'graph_type': graph_type,
                    'title': title
                }
                
                if as_html:
                    result['html'] = f'<img src="data:image/{format};base64,{img_data}" alt="{title or "Graph"}" />'
                
                return result
            else:
                plt.close(fig)
                return {
                    'graph_type': graph_type,
                    'title': title,
                    'format': format
                }
        
        except Exception as e:
            logging.error(f"Error generating graph visualization: {e}")
            return {
                'error': str(e),
                'graph_type': self.graph_type,
                'title': self.title
            }
    
    def _extract_graph_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract graph data from analysis results.
        
        Args:
            analysis_results: Analysis results to extract data from
            
        Returns:
            A dictionary containing nodes and edges for the graph
        """
        nodes = []
        edges = []
        
        # Try to extract dependency information
        if 'dependencies' in analysis_results:
            deps = analysis_results['dependencies']
            if isinstance(deps, dict):
                for source, targets in deps.items():
                    if source not in nodes:
                        nodes.append(source)
                    
                    if isinstance(targets, list):
                        for target in targets:
                            if target not in nodes:
                                nodes.append(target)
                            edges.append((source, target))
                    elif isinstance(targets, str):
                        if targets not in nodes:
                            nodes.append(targets)
                        edges.append((source, targets))
        
        # Try to extract file relationships
        if 'files_added' in analysis_results and 'files_modified' in analysis_results:
            files_added = analysis_results['files_added']
            files_modified = analysis_results['files_modified']
            
            # Group files by directory
            directories = {}
            for file in files_added + files_modified:
                parts = file.split('/')
                if len(parts) > 1:
                    directory = '/'.join(parts[:-1])
                    if directory not in directories:
                        directories[directory] = []
                    directories[directory].append(file)
            
            # Add directories as nodes and files as edges
            for directory, files in directories.items():
                if directory not in nodes:
                    nodes.append(directory)
                
                for file in files:
                    if file not in nodes:
                        nodes.append(file)
                    edges.append((directory, file))
        
        # If no graph data found, try to create a simple graph from issues
        if not nodes and not edges and 'issues' in analysis_results:
            issues = analysis_results['issues']
            if isinstance(issues, list):
                # Group issues by file
                files = {}
                for issue in issues:
                    if isinstance(issue, dict) and 'file' in issue:
                        file = issue['file']
                        if file not in files:
                            files[file] = []
                        files[file].append(issue)
                
                # Add files as nodes and issues as edges
                for file, file_issues in files.items():
                    if file not in nodes:
                        nodes.append(file)
                    
                    for i, issue in enumerate(file_issues):
                        issue_id = f"Issue {i+1}"
                        if issue_id not in nodes:
                            nodes.append(issue_id)
                        edges.append((file, issue_id))
        
        return {
            'nodes': nodes,
            'edges': edges
        }

