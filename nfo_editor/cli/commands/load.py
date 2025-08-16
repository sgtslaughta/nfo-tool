"""
Load Command Implementation

Enhanced load command with Rich formatting and syntax highlighting.
Displays NFO file contents with beautiful formatting and field filtering.

Author: NFO Editor Team
"""

from typing import Tuple, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from ..formatting.syntax import format_nfo_content, highlight_json, highlight_xml
from rich.tree import Tree
from rich.columns import Columns
from rich.text import Text
import json
import yaml
import xml.etree.ElementTree as ET

from nfo_editor import load_nfo_file, NFOError

console = Console()


def load_command(ctx: click.Context, file: str, output_format: str, fields: Tuple[str, ...]):
    """
    Execute the load command with Rich formatting.
    
    Args:
        ctx: Click context
        file: Path to NFO file to load
        output_format: Output format (table, json, yaml)
        fields: Specific fields to display (optional)
    """
    try:
        # Load NFO file data
        result = load_nfo_file(file)
        
        # Format and display results
        if output_format == 'json':
            display_json_output(result, fields)
        elif output_format == 'yaml':
            display_yaml_output(result, fields)
        else:  # table format (default)
            display_table_output(file, result, fields, ctx)
            
    except NFOError as e:
        console.print(f"[red]Error:[/red] {e}")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        ctx.exit(1)


def display_table_output(file_path: str, result: dict, fields: Tuple[str, ...], ctx: Optional[click.Context] = None):
    """
    Display file contents in Rich table format.
    
    Args:
        file_path: Path to the loaded file
        result: Load result dictionary
        fields: Specific fields to show (if any)
    """
    # File info panel
    file_info = (
        f"[bold]File:[/bold] {file_path}\n"
        f"[bold]Format:[/bold] {result['format_type'].upper()}\n"
        f"[bold]Encoding:[/bold] {result['encoding']}\n"
        f"[bold]Modified:[/bold] {'Yes' if result['is_modified'] else 'No'}"
    )
    
    info_panel = Panel(
        file_info,
        title="📄 File Information",
        border_style="blue"
    )
    console.print(info_panel)
    console.print()
    
    # Filter fields if specified
    all_fields = result['all_fields_flat']
    if fields:
        filtered_fields = {}
        for field_filter in fields:
            for field_name, value in all_fields.items():
                if field_filter.lower() in field_name.lower():
                    filtered_fields[field_name] = value
        fields_to_show = filtered_fields
    else:
        fields_to_show = all_fields
    
    if not fields_to_show:
        console.print("[yellow]No fields found matching criteria.[/yellow]")
        return
    
    # Display fields in table
    fields_table = Table(title=f"🏷️ NFO Fields ({len(fields_to_show)})")
    fields_table.add_column("Field", style="cyan", no_wrap=True)
    fields_table.add_column("Value", style="white")
    fields_table.add_column("Type", style="dim", no_wrap=True)
    
    # Sort fields alphabetically
    sorted_fields = sorted(fields_to_show.items())
    
    for field_name, value in sorted_fields:
        # Format value based on type and length
        formatted_value = format_field_value(value)
        value_type = type(value).__name__
        
        fields_table.add_row(field_name, formatted_value, value_type)
    
    console.print(fields_table)
    
    # Show raw content with syntax highlighting
    if not ctx.obj.get('quiet', False):
        display_file_content_preview(file_path, result['format_type'])
    
    # Show nested structure if available
    if result.get('fields') and isinstance(result['fields'], dict):
        display_nested_structure(result['fields'])


def display_json_output(result: dict, fields: Tuple[str, ...]):
    """
    Display results in JSON format with syntax highlighting.
    
    Args:
        result: Load result dictionary  
        fields: Fields to filter (if any)
    """
    # Filter data if fields specified
    if fields:
        filtered_data = filter_fields_data(result, fields)
    else:
        filtered_data = result
    
    # Display with enhanced syntax highlighting
    json_str = json.dumps(filtered_data, indent=2, default=str)
    highlighted_json = highlight_json(json_str, title="📄 NFO Data (JSON)")
    console.print(highlighted_json)


def display_yaml_output(result: dict, fields: Tuple[str, ...]):
    """
    Display results in YAML format with syntax highlighting.
    
    Args:
        result: Load result dictionary
        fields: Fields to filter (if any)  
    """
    # Filter data if fields specified
    if fields:
        filtered_data = filter_fields_data(result, fields)
    else:
        filtered_data = result
    
    # Display with enhanced syntax highlighting
    yaml_str = yaml.dump(filtered_data, default_flow_style=False, allow_unicode=True)
    from ..formatting.syntax import highlight_yaml
    highlighted_yaml = highlight_yaml(yaml_str, title="📄 NFO Data (YAML)")
    console.print(highlighted_yaml)


def format_field_value(value) -> str:
    """
    Format field value for display in table.
    
    Args:
        value: Field value to format
        
    Returns:
        Formatted string representation
    """
    if value is None:
        return "[dim]None[/dim]"
    elif isinstance(value, bool):
        return "✅ True" if value else "❌ False" 
    elif isinstance(value, (list, tuple)):
        if len(value) == 0:
            return "[dim]Empty list[/dim]"
        elif len(value) == 1:
            return f"[{format_field_value(value[0])}]"
        else:
            return f"[{len(value)} items: {format_field_value(value[0])}, ...]"
    elif isinstance(value, dict):
        if not value:
            return "[dim]Empty dict[/dim]"
        else:
            return f"{{dict with {len(value)} keys}}"
    elif isinstance(value, str):
        if len(value) > 100:
            return value[:97] + "..."
        elif '\n' in value:
            return value.replace('\n', '\\n')[:100]
        else:
            return value
    else:
        return str(value)


def display_nested_structure(data: dict, max_depth: int = 3):
    """
    Display nested data structure as a tree.
    
    Args:
        data: Nested data dictionary
        max_depth: Maximum depth to display
    """
    if not isinstance(data, dict) or not data:
        return
    
    tree = Tree("🌳 Nested Structure")
    _build_tree_recursive(tree, data, 0, max_depth)
    
    console.print()
    console.print(tree)


def _build_tree_recursive(parent_node, data, current_depth: int, max_depth: int):
    """
    Recursively build tree structure for nested data.
    
    Args:
        parent_node: Parent tree node
        data: Data to add to tree
        current_depth: Current recursion depth
        max_depth: Maximum depth to recurse
    """
    if current_depth >= max_depth:
        return
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and value:
                branch = parent_node.add(f"📁 {key}")
                _build_tree_recursive(branch, value, current_depth + 1, max_depth)
            elif isinstance(value, list) and value:
                branch = parent_node.add(f"📋 {key} ({len(value)} items)")
                if current_depth < max_depth - 1:
                    for i, item in enumerate(value[:3]):  # Show first 3 items
                        _build_tree_recursive(branch, {f"[{i}]": item}, current_depth + 1, max_depth)
                    if len(value) > 3:
                        branch.add("...")
            else:
                formatted_value = format_field_value(value)
                parent_node.add(f"🏷️ {key}: {formatted_value}")


def filter_fields_data(result: dict, fields: Tuple[str, ...]) -> dict:
    """
    Filter result data based on field patterns.
    
    Args:
        result: Full result dictionary
        fields: Field patterns to match
        
    Returns:
        Filtered result dictionary
    """
    filtered = result.copy()
    
    # Filter flat fields
    if 'all_fields_flat' in filtered:
        filtered_flat = {}
        for field_filter in fields:
            for field_name, value in result['all_fields_flat'].items():
                if field_filter.lower() in field_name.lower():
                    filtered_flat[field_name] = value
        filtered['all_fields_flat'] = filtered_flat
    
    return filtered


def display_file_content_preview(file_path: str, format_type: str):
    """
    Display file content with syntax highlighting.
    
    Args:
        file_path: Path to the file to display
        format_type: Detected format type
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[red]Error reading file:[/red] {e}")
            return
    
    # Use the new syntax highlighting function
    highlighted_content = format_nfo_content(
        content=content,
        format_type=format_type,
        title=f"📄 Raw Content ({format_type.upper()})",
        show_panel=True
    )
    
    console.print()
    console.print(highlighted_content)
