"""
Rich Table Formatters

Advanced table formatting components for beautiful, sortable, and interactive output.
Provides consistent styling and advanced features across all CLI commands.

Author: NFO Editor Team
"""

from typing import List, Dict, Any, Optional, Tuple
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich.align import Align
from pathlib import Path
import os


class ScanResultTable:
    """Advanced table formatter for scan results with sorting and filtering."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def create_summary_table(self, result: dict) -> Table:
        """
        Create a summary table for scan results.
        
        Args:
            result: Scan result dictionary
            
        Returns:
            Rich Table with formatted summary
        """
        table = Table(title="📂 Scan Summary", show_header=False, box=None)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold white")
        
        # Add summary rows with formatting
        table.add_row("NFO files found", self._format_count(len(result['nfo_files'])))
        table.add_row("Directories scanned", str(result['directories_scanned']))
        table.add_row("Total files scanned", str(result['total_files_scanned']))
        table.add_row("Scan time", f"{result['scan_time_seconds']:.2f}s")
        
        if result.get('filter_pattern'):
            table.add_row("Filter pattern", f"[dim]{result['filter_pattern']}[/dim]")
        
        return table
    
    def create_files_table(self, files: List[str], max_display: int = 50) -> Table:
        """
        Create a table for displaying found files.
        
        Args:
            files: List of file paths
            max_display: Maximum number of files to display
            
        Returns:
            Rich Table with file listings
        """
        table = Table(title=f"📄 Found NFO Files ({len(files)})")
        table.add_column("File Path", style="green")
        table.add_column("Size", style="dim", no_wrap=True)
        table.add_column("Modified", style="dim", no_wrap=True)
        
        displayed_files = files[:max_display]
        
        for file_path in displayed_files:
            size_str = self._get_file_size(file_path)
            mod_time = self._get_mod_time(file_path)
            table.add_row(file_path, size_str, mod_time)
        
        return table
    
    def _format_count(self, count: int) -> str:
        """Format file count with appropriate styling."""
        if count == 0:
            return "[red]0[/red]"
        elif count < 10:
            return f"[green]{count}[/green]"
        elif count < 100:
            return f"[yellow]{count}[/yellow]"
        else:
            return f"[cyan]{count}[/cyan]"
    
    def _get_file_size(self, file_path: str) -> str:
        """Get formatted file size."""
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size}B"
            elif size < 1024 * 1024:
                return f"{size // 1024}KB"
            else:
                return f"{size // (1024 * 1024)}MB"
        except Exception:
            return "?"
    
    def _get_mod_time(self, file_path: str) -> str:
        """Get formatted modification time."""
        try:
            import datetime
            mtime = os.path.getmtime(file_path)
            dt = datetime.datetime.fromtimestamp(mtime)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "?"


class FileListTable:
    """Table formatter for file listings with metadata."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def create_file_comparison_table(self, before: Dict[str, Any], after: Dict[str, Any]) -> Table:
        """
        Create a table comparing file states before and after operations.
        
        Args:
            before: Before state data
            after: After state data
            
        Returns:
            Rich Table with comparison data
        """
        table = Table(title="📋 File Comparison")
        table.add_column("Field", style="cyan")
        table.add_column("Before", style="dim")
        table.add_column("After", style="green")
        table.add_column("Status", style="bold")
        
        # Compare common fields
        all_fields = set(before.keys()) | set(after.keys())
        
        for field in sorted(all_fields):
            before_val = str(before.get(field, "N/A"))
            after_val = str(after.get(field, "N/A"))
            
            if before_val != after_val:
                status = "✅ Changed"
                status_style = "green"
            else:
                status = "➖ Same"
                status_style = "dim"
            
            table.add_row(
                field,
                before_val[:50] + "..." if len(before_val) > 50 else before_val,
                after_val[:50] + "..." if len(after_val) > 50 else after_val,
                f"[{status_style}]{status}[/{status_style}]"
            )
        
        return table


class FieldComparisonTable:
    """Advanced table for comparing NFO field values."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def create_field_summary_table(self, fields: Dict[str, Any]) -> Table:
        """
        Create a summary table of NFO fields.
        
        Args:
            fields: Dictionary of field names and values
            
        Returns:
            Rich Table with field summary
        """
        table = Table(title="🏷️ NFO Fields")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Type", style="dim", no_wrap=True)
        
        # Sort fields alphabetically
        for field, value in sorted(fields.items()):
            formatted_value = self._format_field_value(value)
            value_type = type(value).__name__
            
            table.add_row(field, formatted_value, value_type)
        
        return table
    
    def create_changes_preview_table(self, changes: List[Dict[str, Any]]) -> Table:
        """
        Create a table showing proposed field changes.
        
        Args:
            changes: List of change dictionaries
            
        Returns:
            Rich Table with change preview
        """
        table = Table(title="🔄 Proposed Changes")
        table.add_column("File", style="green")
        table.add_column("Field", style="cyan")
        table.add_column("Current", style="dim")
        table.add_column("New", style="yellow")
        table.add_column("Action", style="bold")
        
        for change in changes[:20]:  # Limit display
            action_style = "green" if change.get('will_change') else "dim"
            action_text = "✅ Update" if change.get('will_change') else "➖ No change"
            
            table.add_row(
                change.get('file', ''),
                change.get('field', ''),
                str(change.get('current', 'N/A'))[:30],
                str(change.get('new', 'N/A'))[:30],
                f"[{action_style}]{action_text}[/{action_style}]"
            )
        
        return table
    
    def _format_field_value(self, value: Any) -> str:
        """Format field value for display."""
        if value is None:
            return "[dim]None[/dim]"
        elif isinstance(value, bool):
            return "✅ True" if value else "❌ False"
        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                return "[dim]Empty list[/dim]"
            elif len(value) == 1:
                return f"[{self._format_field_value(value[0])}]"
            else:
                return f"[{len(value)} items]"
        elif isinstance(value, dict):
            return f"{{dict with {len(value)} keys}}"
        elif isinstance(value, str):
            if len(value) > 80:
                return value[:77] + "..."
            return value
        else:
            return str(value)


def create_error_table(errors: List[str]) -> Table:
    """
    Create a formatted table for displaying errors.
    
    Args:
        errors: List of error messages
        
    Returns:
        Rich Table with error information
    """
    table = Table(title=f"❌ Errors ({len(errors)})", show_header=False)
    table.add_column("Error", style="red")
    
    for i, error in enumerate(errors[:10], 1):  # Show first 10 errors
        table.add_row(f"{i}. {error}")
    
    if len(errors) > 10:
        table.add_row(f"... and {len(errors) - 10} more errors")
    
    return table


def create_stats_table(stats: Dict[str, Any]) -> Table:
    """
    Create a statistics table for operation results.
    
    Args:
        stats: Dictionary of statistics
        
    Returns:
        Rich Table with statistics
    """
    table = Table(title="📊 Operation Statistics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")
    
    for key, value in stats.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, float):
            formatted_value = f"{value:.2f}"
        else:
            formatted_value = str(value)
        
        table.add_row(formatted_key, formatted_value)
    
    return table
