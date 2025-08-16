"""
Edit Command Implementation

Enhanced edit command with Rich formatting, progress bars, and field validation.
Supports dry-run mode and backup creation.

Author: NFO Editor Team
"""

from typing import Optional, Tuple, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import json
import time

from nfo_editor import edit_nfo_files, NFOError

console = Console()


def edit_command(ctx: click.Context, directories: Tuple[str, ...], 
                field_updates: Tuple[str, ...], pattern: Optional[str],
                output_format: Optional[str], backup: bool, dry_run: bool,
                max_files: Optional[int]):
    """
    Execute the edit command with Rich formatting.
    
    Args:
        ctx: Click context
        directories: Directories to process
        field_updates: Field update strings (field=value)
        pattern: Optional file pattern filter
        output_format: Output format for files
        backup: Whether to create backups
        dry_run: Preview mode without applying changes
        max_files: Maximum number of files to process
    """
    try:
        # Parse field updates
        parsed_updates = parse_field_updates(field_updates)
        
        if not parsed_updates:
            console.print("[red]Error:[/red] No field updates specified. Use --set field=value")
            ctx.exit(1)
        
        # Execute edit operation with progress tracking
        if not dry_run and not ctx.obj.get('quiet', False):
            result = execute_edit_with_progress(
                directories=list(directories),
                field_updates=parsed_updates,
                backup=backup,
                file_pattern=pattern,
                output_format=output_format,
                max_files=max_files
            )
        else:
            result = edit_nfo_files(
                directories=list(directories),
                field_updates=parsed_updates,
                backup=backup,
                dry_run=dry_run,
                file_pattern=pattern,
                output_format=output_format,
                max_files=max_files
            )
        
        # Display results
        display_edit_results(result, dry_run)
        
    except NFOError as e:
        console.print(f"[red]Error:[/red] {e}")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        ctx.exit(1)


def parse_field_updates(field_updates: Tuple[str, ...]) -> Dict[str, Any]:
    """
    Parse field update strings into a dictionary.
    
    Args:
        field_updates: Tuple of "field=value" strings
        
    Returns:
        Dictionary of field updates
    """
    updates = {}
    
    for update in field_updates:
        if '=' not in update:
            console.print(f"[red]Error:[/red] Invalid field update format: {update}")
            console.print("Use format: field=value")
            continue
        
        field, value = update.split('=', 1)
        field = field.strip()
        value = value.strip()
        
        # Try to convert value to appropriate type
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        updates[field] = value
    
    return updates


def display_edit_results(result: dict, dry_run: bool):
    """
    Display edit results in Rich format.
    
    Args:
        result: Edit result dictionary
        dry_run: Whether this was a dry run
    """
    # Create summary table
    mode_title = "🔍 Edit Preview (Dry Run)" if dry_run else "✏️ Edit Results"
    summary_table = Table(title=mode_title, show_header=False)
    summary_table.add_column("Property", style="cyan")
    summary_table.add_column("Value", style="bold")
    
    if dry_run:
        summary_table.add_row("Files that would be processed", str(result.get('files_previewed', 0)))
    else:
        summary_table.add_row("Total files", str(result['total_files']))
        summary_table.add_row("Successful edits", str(result['successful_edits']))
        summary_table.add_row("Failed edits", str(result['failed_edits']))
        summary_table.add_row("Execution time", f"{result['execution_time_seconds']:.2f}s")
    
    console.print(summary_table)
    console.print()
    
    # Display errors if any
    if result.get('errors'):
        console.print(f"[red]Errors ({len(result['errors'])}):[/red]")
        for error in result['errors']:
            console.print(f"  ❌ {error}")
        console.print()
    
    # Display individual file results
    if dry_run and 'file_previews' in result:
        display_preview_results(result['file_previews'])
    elif not dry_run and 'results' in result:
        display_file_results(result['results'])


def display_preview_results(previews: list):
    """Display dry-run preview results."""
    if not previews:
        return
        
    preview_table = Table(title="📋 Preview Changes")
    preview_table.add_column("File", style="green")
    preview_table.add_column("Format", style="blue")
    preview_table.add_column("Changes", style="yellow")
    
    for preview in previews[:20]:  # Limit display
        if 'error' in preview:
            preview_table.add_row(preview['file_path'], "Error", preview['error'])
        else:
            changes = []
            for field, change in preview.get('field_changes', {}).items():
                if change['will_change']:
                    changes.append(f"{field}: {change['current']} → {change['new']}")
            
            preview_table.add_row(
                preview['file_path'],
                preview.get('format', 'unknown'),
                '\n'.join(changes) if changes else "No changes"
            )
    
    console.print(preview_table)
    
    if len(previews) > 20:
        console.print(f"[yellow]Note:[/yellow] Showing first 20 of {len(previews)} files.")


def display_file_results(results: list):
    """Display actual edit results."""
    if not results:
        return
        
    # Show only failed results unless verbose
    failed_results = [r for r in results if not r['success']]
    
    if failed_results:
        console.print("[red]Failed Files:[/red]")
        for result in failed_results:
            console.print(f"  ❌ {result['file_path']}")
            for error in result.get('errors', []):
                console.print(f"    Error: {error}")
    
    success_count = len([r for r in results if r['success']])
    if success_count > 0:
        console.print(f"[green]✅ Successfully processed {success_count} files[/green]")


def execute_edit_with_progress(directories: list, field_updates: Dict[str, Any],
                             backup: bool, file_pattern: Optional[str], 
                             output_format: Optional[str], max_files: Optional[int]) -> dict:
    """
    Execute edit operation with Rich progress tracking.
    
    Args:
        directories: Directories to process
        field_updates: Field updates to apply
        backup: Whether to create backups
        file_pattern: Optional file pattern filter
        output_format: Output format for files
        max_files: Maximum number of files to process
        
    Returns:
        Edit operation results
    """
    # Create progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        refresh_per_second=4
    ) as progress:
        
        # Add overall progress task
        overall_task = progress.add_task(
            "[cyan]Editing NFO files...", 
            total=100
        )
        
        # Simulate progress tracking (in real implementation, this would be integrated with the core library)
        console.print(Panel(
            "[yellow]🚧 Progress tracking integration coming soon![/yellow]\n"
            "Currently showing simulated progress for demonstration.",
            title="Progress Demo",
            border_style="yellow"
        ))
        
        # Show progress simulation
        for i in range(101):
            progress.update(overall_task, completed=i)
            time.sleep(0.02)  # Simulate work
            
            if i == 25:
                progress.update(overall_task, description="[cyan]Scanning for NFO files...")
            elif i == 50:
                progress.update(overall_task, description="[cyan]Processing files...")
            elif i == 75:
                progress.update(overall_task, description="[cyan]Creating backups...")
            elif i == 95:
                progress.update(overall_task, description="[cyan]Finalizing...")
        
        progress.update(overall_task, description="[green]✅ Edit operation completed!")
        time.sleep(0.5)  # Show completion
    
    # Execute actual edit operation
    return edit_nfo_files(
        directories=directories,
        field_updates=field_updates,
        backup=backup,
        dry_run=False,
        file_pattern=file_pattern,
        output_format=output_format,
        max_files=max_files
    )
