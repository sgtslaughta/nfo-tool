"""
Detect Command Implementation

Enhanced detect command with Rich formatting and syntax highlighting.
Analyzes NFO files to determine format with confidence scoring.

Author: NFO Editor Team
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json

from nfo_editor import detect_nfo_format, NFOError

console = Console()


def detect_command(ctx: click.Context, file: str, output_format: str):
    """
    Execute the detect command with Rich formatting.
    
    Args:
        ctx: Click context
        file: Path to NFO file to analyze
        output_format: Output format (table, json)
    """
    try:
        # Execute format detection
        result = detect_nfo_format(file)
        
        # Format and display results
        if output_format == 'json':
            console.print(json.dumps(result, indent=2))
        else:  # table format (default)
            display_detection_table(file, result, ctx.obj.get('verbose', False))
            
    except NFOError as e:
        console.print(f"[red]Error:[/red] {e}")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        ctx.exit(1)


def display_detection_table(file_path: str, result: dict, verbose: bool):
    """
    Display format detection results in Rich table format.
    
    Args:
        file_path: Path to the analyzed file
        result: Detection result dictionary
        verbose: Whether to show detailed information
    """
    # File info panel
    file_panel = Panel(
        f"[bold]File:[/bold] {file_path}",
        title="🔍 Format Detection",
        border_style="blue"
    )
    console.print(file_panel)
    console.print()
    
    # Main detection results
    detection_table = Table(title="Detection Results", show_header=False)
    detection_table.add_column("Property", style="cyan")
    detection_table.add_column("Value", style="bold")
    
    # Format with confidence indicator
    confidence = result['confidence']
    confidence_style = "green" if confidence > 0.8 else "yellow" if confidence > 0.5 else "red"
    confidence_indicator = "🔴" if confidence < 0.5 else "🟡" if confidence < 0.8 else "🟢"
    
    detection_table.add_row(
        "Detected Format", 
        f"[{confidence_style}]{result['format'].upper()}[/{confidence_style}]"
    )
    detection_table.add_row(
        "Confidence",
        f"{confidence_indicator} {confidence:.1%}"
    )
    detection_table.add_row("Encoding", result['encoding'])
    
    if result.get('fallback_formats'):
        fallback_formats = ', '.join([fmt.upper() for fmt in result['fallback_formats']])
        detection_table.add_row("Fallback Formats", fallback_formats)
    
    console.print(detection_table)
    console.print()
    
    # Show detailed analysis if verbose
    if verbose and result.get('details'):
        show_detection_details(result['details'])
    
    # Show confidence interpretation
    show_confidence_help(confidence)


def show_detection_details(details: dict):
    """
    Show detailed detection analysis.
    
    Args:
        details: Detection details dictionary
    """
    if not details:
        return
        
    details_table = Table(title="🔬 Analysis Details")
    details_table.add_column("Check", style="cyan")
    details_table.add_column("Result", style="bold")
    
    for check, value in details.items():
        # Format the value based on type
        if isinstance(value, bool):
            formatted_value = "✅ Pass" if value else "❌ Fail"
        elif isinstance(value, (int, float)):
            formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
        else:
            formatted_value = str(value)
            
        details_table.add_row(check.replace('_', ' ').title(), formatted_value)
    
    console.print(details_table)
    console.print()


def show_confidence_help(confidence: float):
    """
    Show interpretation of confidence score.
    
    Args:
        confidence: Confidence score (0.0 to 1.0)
    """
    if confidence >= 0.8:
        message = "[green]High confidence - Format detection is very reliable[/green]"
    elif confidence >= 0.5:
        message = "[yellow]Medium confidence - Format likely correct but verify[/yellow]"  
    else:
        message = "[red]Low confidence - Manual verification recommended[/red]"
    
    confidence_panel = Panel(
        message,
        title="💡 Confidence Level",
        border_style="dim"
    )
    console.print(confidence_panel)
