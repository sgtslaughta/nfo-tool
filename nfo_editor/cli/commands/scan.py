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
import json

from nfo_editor import scan_nfo_files, NFOError
from ..formatting.progress import BatchProgressTracker, OperationType
from ..formatting.tables import ScanResultTable

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
    # Create progress tracker
    tracker = BatchProgressTracker(
        console=console,
        operation_type=OperationType.SCAN,
        show_speed=False,
        show_eta=True
    )
    
    # Use progress tracking context manager
    with tracker.track_operation(
        total_items=len(directories),
        operation_description="Scanning directories for NFO files",
        show_summary=True
    ) as progress_tracker:
        
        # Scan each directory with progress updates
        all_results = {
            'nfo_files': [],
            'directories_scanned': 0,
            'total_files_scanned': 0,
            'errors': [],
            'scan_time_seconds': 0.0
        }
        
        for i, directory in enumerate(directories, 1):
            try:
                # Update progress with current directory
                progress_tracker.update_progress(
                    completed=0,  # Don't advance yet
                    current_item=f"Scanning {directory}"
                )
                
                # Execute scan for this directory
                dir_result = scan_nfo_files(
                    directories=[directory],
                    pattern=pattern,
                    recursive=recursive
                )
                
                # Aggregate results
                all_results['nfo_files'].extend(dir_result.get('nfo_files', []))
                all_results['directories_scanned'] += dir_result.get('directories_scanned', 0)
                all_results['total_files_scanned'] += dir_result.get('total_files_scanned', 0)
                all_results['errors'].extend(dir_result.get('errors', []))
                all_results['scan_time_seconds'] += dir_result.get('scan_time_seconds', 0.0)
                
                # Update progress as completed
                progress_tracker.update_progress(
                    completed=1,
                    current_item=f"✅ {directory} ({len(dir_result.get('nfo_files', []))} files)"
                )
                
            except Exception as e:
                error_msg = f"Error scanning {directory}: {str(e)}"
                progress_tracker.add_error(error_msg, directory)
                all_results['errors'].append(error_msg)
                
                # Still advance progress for failed directory
                progress_tracker.update_progress(
                    completed=1,
                    current_item=f"❌ {directory} (failed)"
                )
        
        return all_results
