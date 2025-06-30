"""
Table Visualization Module

This module provides a visualization for generating tables from analysis results.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from .base_visualization import BaseVisualization


class TableVisualization(BaseVisualization):
    """
    Visualization for generating tables from analysis results.
    
    This visualization can generate HTML, Markdown, or plain text tables
    from analysis results.
    """
    
    def __init__(
        self,
        format: str = 'html',
        headers: Optional[List[str]] = None,
        caption: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_reverse: bool = False
    ):
        """
        Initialize a new TableVisualization.
        
        Args:
            format: Table format ('html', 'markdown', 'text')
            headers: Table headers
            caption: Table caption
            sort_by: Column to sort by
            sort_reverse: Whether to sort in reverse order
        """
        self.format = format
        self.headers = headers
        self.caption = caption
        self.sort_by = sort_by
        self.sort_reverse = sort_reverse
        
    def generate(
        self, 
        analysis_results: Dict[str, Any], 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a table visualization from analysis results.
        
        Args:
            analysis_results: Analysis results to visualize
            **kwargs: Additional visualization-specific arguments, including:
                - data_key: Key in analysis_results containing the data to visualize
                - headers: Override the default table headers
                - caption: Override the default table caption
                - format: Override the default table format
                - sort_by: Override the default sort column
                - sort_reverse: Override the default sort order
                - max_rows: Maximum number of rows to include
                - include_row_numbers: Whether to include row numbers
                - table_class: CSS class for the HTML table
                - table_id: ID for the HTML table
            
        Returns:
            A dictionary containing the visualization data, including:
                - table: The generated table
                - format: The table format
                - headers: The table headers
                - caption: The table caption
                - row_count: The number of rows in the table
        """
        try:
            # Get table parameters
            data_key = kwargs.get('data_key')
            headers = kwargs.get('headers', self.headers)
            caption = kwargs.get('caption', self.caption)
            format = kwargs.get('format', self.format)
            sort_by = kwargs.get('sort_by', self.sort_by)
            sort_reverse = kwargs.get('sort_reverse', self.sort_reverse)
            max_rows = kwargs.get('max_rows')
            include_row_numbers = kwargs.get('include_row_numbers', False)
            table_class = kwargs.get('table_class', 'table table-striped')
            table_id = kwargs.get('table_id')
            
            # Extract the data to visualize
            data = self._extract_data(analysis_results, data_key)
            
            if not data:
                logging.warning("No data to visualize")
                return {
                    'error': "No data to visualize",
                    'format': format,
                    'caption': caption
                }
            
            # Convert the data to a list of rows
            rows = self._convert_to_rows(data)
            
            # Determine headers if not provided
            if not headers and rows:
                if isinstance(rows[0], dict):
                    headers = list(rows[0].keys())
                elif isinstance(rows[0], (list, tuple)):
                    headers = [f"Column {i+1}" for i in range(len(rows[0]))]
            
            # Sort the rows if requested
            if sort_by and headers:
                try:
                    sort_index = headers.index(sort_by)
                    rows.sort(key=lambda row: row[sort_index] if isinstance(row, (list, tuple)) else row.get(sort_by, ''),
                              reverse=sort_reverse)
                except (ValueError, IndexError):
                    pass
            
            # Limit the number of rows if requested
            if max_rows and len(rows) > max_rows:
                rows = rows[:max_rows]
            
            # Add row numbers if requested
            if include_row_numbers:
                if headers:
                    headers = ['#'] + list(headers)
                
                for i, row in enumerate(rows):
                    if isinstance(row, dict):
                        row = {'#': i + 1, **row}
                    elif isinstance(row, (list, tuple)):
                        row = [i + 1] + list(row)
                    rows[i] = row
            
            # Generate the table based on the format
            if format == 'html':
                table = self._generate_html_table(rows, headers, caption, table_class, table_id)
            elif format == 'markdown':
                table = self._generate_markdown_table(rows, headers, caption)
            elif format == 'text':
                table = self._generate_text_table(rows, headers, caption)
            else:
                logging.warning(f"Unsupported table format: {format}")
                return {
                    'error': f"Unsupported table format: {format}",
                    'format': format,
                    'caption': caption
                }
            
            return {
                'table': table,
                'format': format,
                'headers': headers,
                'caption': caption,
                'row_count': len(rows)
            }
        
        except Exception as e:
            logging.error(f"Error generating table visualization: {e}")
            return {
                'error': str(e),
                'format': self.format,
                'caption': self.caption
            }
    
    def _extract_data(
        self, 
        analysis_results: Dict[str, Any], 
        data_key: Optional[str] = None
    ) -> Any:
        """
        Extract data from analysis results for visualization.
        
        Args:
            analysis_results: Analysis results to extract data from
            data_key: Key in analysis_results containing the data to visualize
            
        Returns:
            The extracted data
        """
        if data_key and data_key in analysis_results:
            # Use the specified data key
            return analysis_results[data_key]
        
        # Try to find suitable data
        for key in ['issues', 'metrics', 'files_added', 'files_modified', 'files_removed']:
            if key in analysis_results and analysis_results[key]:
                return analysis_results[key]
        
        # No suitable data found
        return None
    
    def _convert_to_rows(self, data: Any) -> List[Any]:
        """
        Convert data to a list of rows for the table.
        
        Args:
            data: Data to convert
            
        Returns:
            A list of rows
        """
        if isinstance(data, list):
            # If it's already a list, use it directly
            return data
        elif isinstance(data, dict):
            # Convert dictionary to list of rows
            if all(isinstance(value, dict) for value in data.values()):
                # Dictionary of dictionaries
                return [{'key': key, **value} for key, value in data.items()]
            else:
                # Simple dictionary
                return [{'key': key, 'value': value} for key, value in data.items()]
        else:
            # Unsupported data format
            return []
    
    def _generate_html_table(
        self, 
        rows: List[Any], 
        headers: Optional[List[str]] = None,
        caption: Optional[str] = None,
        table_class: str = 'table table-striped',
        table_id: Optional[str] = None
    ) -> str:
        """
        Generate an HTML table.
        
        Args:
            rows: Table rows
            headers: Table headers
            caption: Table caption
            table_class: CSS class for the table
            table_id: ID for the table
            
        Returns:
            The HTML table as a string
        """
        html_parts = []
        
        # Start the table
        html_parts.append(f'<table class="{table_class}"' + (f' id="{table_id}"' if table_id else '') + '>')
        
        # Add caption if provided
        if caption:
            html_parts.append(f'  <caption>{caption}</caption>')
        
        # Add headers if provided
        if headers:
            html_parts.append('  <thead>')
            html_parts.append('    <tr>')
            for header in headers:
                html_parts.append(f'      <th>{header}</th>')
            html_parts.append('    </tr>')
            html_parts.append('  </thead>')
        
        # Add rows
        html_parts.append('  <tbody>')
        for row in rows:
            html_parts.append('    <tr>')
            
            if isinstance(row, dict):
                # Dictionary row
                for header in (headers or row.keys()):
                    value = row.get(header, '')
                    html_parts.append(f'      <td>{value}</td>')
            elif isinstance(row, (list, tuple)):
                # List row
                for value in row:
                    html_parts.append(f'      <td>{value}</td>')
            else:
                # Single value row
                html_parts.append(f'      <td>{row}</td>')
            
            html_parts.append('    </tr>')
        html_parts.append('  </tbody>')
        
        # End the table
        html_parts.append('</table>')
        
        return '\n'.join(html_parts)
    
    def _generate_markdown_table(
        self, 
        rows: List[Any], 
        headers: Optional[List[str]] = None,
        caption: Optional[str] = None
    ) -> str:
        """
        Generate a Markdown table.
        
        Args:
            rows: Table rows
            headers: Table headers
            caption: Table caption
            
        Returns:
            The Markdown table as a string
        """
        md_parts = []
        
        # Add caption if provided
        if caption:
            md_parts.append(f"**{caption}**")
            md_parts.append("")
        
        # Determine column widths
        col_widths = []
        if headers:
            col_widths = [len(str(header)) for header in headers]
        
        # Update column widths based on row values
        for row in rows:
            if isinstance(row, dict):
                # Dictionary row
                for i, header in enumerate(headers or []):
                    value = str(row.get(header, ''))
                    if i >= len(col_widths):
                        col_widths.append(len(value))
                    else:
                        col_widths[i] = max(col_widths[i], len(value))
            elif isinstance(row, (list, tuple)):
                # List row
                for i, value in enumerate(row):
                    value_str = str(value)
                    if i >= len(col_widths):
                        col_widths.append(len(value_str))
                    else:
                        col_widths[i] = max(col_widths[i], len(value_str))
        
        # Ensure we have at least one column width
        if not col_widths:
            col_widths = [10]
        
        # Add headers if provided
        if headers:
            header_row = "| " + " | ".join(str(header).ljust(col_widths[i]) for i, header in enumerate(headers)) + " |"
            md_parts.append(header_row)
            
            # Add separator row
            separator_row = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
            md_parts.append(separator_row)
        
        # Add rows
        for row in rows:
            if isinstance(row, dict):
                # Dictionary row
                values = [str(row.get(header, '')).ljust(col_widths[i]) for i, header in enumerate(headers or [])]
                md_parts.append("| " + " | ".join(values) + " |")
            elif isinstance(row, (list, tuple)):
                # List row
                values = [str(value).ljust(col_widths[i]) for i, value in enumerate(row)]
                md_parts.append("| " + " | ".join(values) + " |")
            else:
                # Single value row
                md_parts.append("| " + str(row).ljust(col_widths[0]) + " |")
        
        return "\n".join(md_parts)
    
    def _generate_text_table(
        self, 
        rows: List[Any], 
        headers: Optional[List[str]] = None,
        caption: Optional[str] = None
    ) -> str:
        """
        Generate a plain text table.
        
        Args:
            rows: Table rows
            headers: Table headers
            caption: Table caption
            
        Returns:
            The plain text table as a string
        """
        text_parts = []
        
        # Add caption if provided
        if caption:
            text_parts.append(caption)
            text_parts.append("")
        
        # Determine column widths
        col_widths = []
        if headers:
            col_widths = [len(str(header)) for header in headers]
        
        # Update column widths based on row values
        for row in rows:
            if isinstance(row, dict):
                # Dictionary row
                for i, header in enumerate(headers or []):
                    value = str(row.get(header, ''))
                    if i >= len(col_widths):
                        col_widths.append(len(value))
                    else:
                        col_widths[i] = max(col_widths[i], len(value))
            elif isinstance(row, (list, tuple)):
                # List row
                for i, value in enumerate(row):
                    value_str = str(value)
                    if i >= len(col_widths):
                        col_widths.append(len(value_str))
                    else:
                        col_widths[i] = max(col_widths[i], len(value_str))
        
        # Ensure we have at least one column width
        if not col_widths:
            col_widths = [10]
        
        # Create the separator line
        separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
        
        # Add the separator
        text_parts.append(separator)
        
        # Add headers if provided
        if headers:
            header_row = "| " + " | ".join(str(header).ljust(col_widths[i]) for i, header in enumerate(headers)) + " |"
            text_parts.append(header_row)
            text_parts.append(separator)
        
        # Add rows
        for row in rows:
            if isinstance(row, dict):
                # Dictionary row
                values = [str(row.get(header, '')).ljust(col_widths[i]) for i, header in enumerate(headers or [])]
                text_parts.append("| " + " | ".join(values) + " |")
            elif isinstance(row, (list, tuple)):
                # List row
                values = [str(value).ljust(col_widths[i]) for i, value in enumerate(row)]
                text_parts.append("| " + " | ".join(values) + " |")
            else:
                # Single value row
                text_parts.append("| " + str(row).ljust(col_widths[0]) + " |")
        
        # Add the final separator
        text_parts.append(separator)
        
        return "\n".join(text_parts)

