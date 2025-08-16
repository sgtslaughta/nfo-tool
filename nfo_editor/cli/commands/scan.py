"""
Scan Command Implementation

Enhanced scan command with Rich formatting for beautiful table output.
Supports pattern filtering and recursive directory scanning.

Author: NFO Editor Team
"""

from typing import Optional, Tuple
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
import json
import time

from nfo_editor import scan_nfo_files, NFOError

console = Console()


def scan_command(ctx: click.Context, directories: Tuple[str, ...], 
                pattern: Optional[str], recursive: bool, output_format: str):
    """
    Execute the scan command with Rich formatting.
    
    Args:
        ctx: Click context
        directories: Directories to scan
        pattern: Optional file pattern filter
        recursive: Whether to scan recursively
        output_format: Output format (table, json, list)
    """
    try:
        # Execute scan operation with progress tracking
        if not ctx.obj.get('quiet', False) and len(directories) > 1:
            result = execute_scan_with_progress(
                directories=list(directories),
                pattern=pattern,
                recursive=recursive
            )
        else:
            result = scan_nfo_files(
                directories=list(directories),
                pattern=pattern,
                recursive=recursive
            )
        
        # Format and display results
        if output_format == 'json':
            console.print(json.dumps(result, indent=2))
        elif output_format == 'list':
            for file_path in result['nfo_files']:
                console.print(file_path)
        else:  # table format (default)
            display_scan_table(result)
            
    except NFOError as e:
        console.print(f"[red]Error:[/red] {e}")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        ctx.exit(1)


def display_scan_table(result: dict):
    """
    Display scan results in a Rich table format.
    
    Args:
        result: Scan result dictionary
    """
    # Create summary table
    summary_table = Table(title="📂 Scan Summary", show_header=False)
    summary_table.add_column("Property", style="cyan")
    summary_table.add_column("Value", style="bold")
    
    summary_table.add_row("NFO files found", str(len(result['nfo_files'])))
    summary_table.add_row("Directories scanned", str(result['directories_scanned']))
    summary_table.add_row("Total files scanned", str(result['total_files_scanned']))
    summary_table.add_row("Scan time", f"{result['scan_time_seconds']:.2f}s")
    
    console.print(summary_table)
    console.print()
    
    # Display errors if any
    if result['errors']:
        console.print(f"[red]Errors ({len(result['errors'])}):[/red]")
        for error in result['errors']:
            console.print(f"  ❌ {error}")
        console.print()
    
    # Display file list if not too many
    if result['nfo_files'] and len(result['nfo_files']) <= 50:
        files_table = Table(title="📄 Found NFO Files")
        files_table.add_column("File Path", style="green")
        
        for file_path in result['nfo_files']:
            files_table.add_row(file_path)
            
        console.print(files_table)
    elif len(result['nfo_files']) > 50:
        console.print(f"[yellow]Note:[/yellow] Found {len(result['nfo_files'])} files. "
                     f"Use --format=list to see all files.")


def execute_scan_with_progress(directories: list, pattern: Optional[str], recursive: bool) -> dict:
    """
    Execute scan operation with Rich progress tracking.
    
    Args:
        directories: Directories to scan
        pattern: Optional file pattern filter
        recursive: Whether to scan recursively
        
    Returns:
        Scan operation results
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=4
    ) as progress:
        
        # Add progress task for each directory
        total_dirs = len(directories)
        overall_task = progress.add_task(
            f"[cyan]Scanning {total_dirs} directories...",
            total=total_dirs
        )
        
        # Simulate progress for demonstration
        console.print(Panel(
            "[yellow]🚧 Enhanced progress tracking coming soon![/yellow]\n"
            "Currently showing simulated progress for multiple directories.",
            title="Progress Demo",
            border_style="yellow"
        ))
        
        for i, directory in enumerate(directories):
            progress.update(
                overall_task, 
                completed=i,
                description=f"[cyan]Scanning {directory}..."
            )
            time.sleep(0.3)  # Simulate directory scan time
        
        progress.update(
            overall_task, 
            completed=total_dirs,
            description="[green]✅ Scan completed!"
        )
        time.sleep(0.5)
    
    # Execute actual scan operation
    return scan_nfo_files(
        directories=directories,
        pattern=pattern,
        recursive=recursive
    )
