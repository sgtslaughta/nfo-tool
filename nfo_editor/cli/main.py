"""
Main CLI Entry Point for NFO Editor

This module implements the modern Click-based CLI with interactive mode as default.
When run without arguments, it launches the interactive TUI. With arguments, it
provides enhanced CLI commands with Rich output formatting.

Key Features:
- Interactive mode is the default behavior
- Flag-based CLI commands (--scan, --edit, --detect, --load)
- YAML configuration support
- Rich formatting for all output modes
- Backward compatibility with existing scripts

Author: NFO Editor Team
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import core NFO Editor functionality
from nfo_editor import (
    edit_nfo_files, scan_nfo_files, detect_nfo_format, load_nfo_file,
    NFOEditor, NFOError
)

# Import new CLI components
try:
    from .interactive.app import NFOEditorApp
    INTERACTIVE_AVAILABLE = True
except ImportError:
    INTERACTIVE_AVAILABLE = False

# Import configuration system
from .config.loader import ConfigLoader, ConfigError
from .config.schemas import NFOEditorConfig
from .formatting.themes import get_theme, set_theme

# Import CLI commands
from .commands.scan import scan_command
from .commands.edit import edit_command
from .commands.detect import detect_command  
from .commands.load import load_command

# Global Rich console for output
console = Console()


def detect_mode(ctx: click.Context) -> str:
    """
    Detect whether to use interactive or CLI mode based on arguments and environment.
    
    Args:
        ctx: Click context with parsed arguments
        
    Returns:
        Mode string: 'interactive' or 'cli'
    """
    # Check environment variable override
    env_mode = os.environ.get('NFO_EDITOR_MODE', '').lower()
    if env_mode in ('cli', 'interactive'):
        return env_mode
    
    # If any command flags are provided, use CLI mode
    cli_flags = [
        '--scan', '--edit', '--detect', '--load',
        '--config', '--generate-config', '--help', '--version'
    ]
    
    if any(flag in sys.argv for flag in cli_flags):
        return 'cli'
    
    # If positional arguments are provided (legacy compatibility)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        return 'cli'
    
    # Default to interactive mode
    return 'interactive'


def show_welcome_banner():
    """Display welcome banner for CLI mode."""
    banner = Panel(
        Text("🎬 NFO Editor v2.0", style="bold blue"),
        subtitle="Interactive NFO File Manager",
        border_style="blue"
    )
    console.print(banner)
    console.print()


@click.command()
@click.option('--config', '-c', 
              type=click.Path(exists=True),
              help='Path to YAML configuration file')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='Enable verbose output')
@click.option('--quiet', '-q', 
              is_flag=True, 
              help='Suppress non-error output')
@click.option('--theme', 
              type=click.Choice(['auto', 'dark', 'light', 'monokai']),
              default='auto',
              help='Color theme for output')
@click.option('--generate-config',
              is_flag=True,
              help='Generate example configuration file')
@click.option('--list-profiles',
              is_flag=True,
              help='List available configuration profiles')
@click.option('--profile',
              help='Use specific configuration profile')
@click.option('--validate-config',
              is_flag=True,
              help='Validate configuration file and exit')
@click.option('--show-config-locations',
              is_flag=True,
              help='Show configuration file search locations')
@click.option('--scan', 'scan_directories', multiple=True,
              help='Scan directories for NFO files')
@click.option('--pattern', help='Glob pattern to filter files (with --scan)')
@click.option('--no-recursive', is_flag=True, 
              help='Disable recursive scanning (with --scan)')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'json', 'list', 'yaml']),
              help='Output format for results')
@click.option('--edit', 'edit_directories', multiple=True,
              help='Edit NFO files in directories')
@click.option('--set', 'field_updates', multiple=True,
              help='Field updates in format field=value (with --edit)')
@click.option('--output-format', 'edit_output_format',
              type=click.Choice(['xml', 'json', 'text']),
              default=None,
              help='Output format for edited files (with --edit)')
@click.option('--backup/--no-backup', default=True,
              help='Create backup files (with --edit)')
@click.option('--dry-run', is_flag=True,
              help='Preview changes without applying (with --edit)')
@click.option('--max-files', type=int,
              help='Maximum files to process (with --edit)')
@click.option('--detect', 'detect_file', type=click.Path(),
              help='Detect format of specific NFO file')
@click.option('--load', 'load_file', type=click.Path(),
              help='Load and display NFO file contents')
@click.option('--fields', multiple=True,
              help='Specific fields to display (with --load)')
@click.version_option(version="2.0.0", prog_name="nfo-editor")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool, quiet: bool, 
        theme: str, generate_config: bool, list_profiles: bool, profile: Optional[str],
        validate_config: bool, show_config_locations: bool,
        scan_directories: Tuple[str, ...], pattern: Optional[str], no_recursive: bool, 
        output_format: Optional[str], edit_directories: Tuple[str, ...], 
        field_updates: Tuple[str, ...], edit_output_format: Optional[str], backup: bool, 
        dry_run: bool, max_files: Optional[int], detect_file: Optional[str], 
        load_file: Optional[str], fields: Tuple[str, ...]):
    """
    NFO Editor - Modern NFO File Manager
    
    Run without arguments for interactive mode, or use flags for CLI mode.
    
    Examples:
        nfo-editor                           # Interactive mode (default)
        nfo-editor --scan /media/movies      # CLI scan command  
        nfo-editor --edit /media --set year=2024  # CLI edit command
        nfo-editor --config workflow.yaml   # Use configuration file
    """
    # Initialize context object
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    ctx.obj['config_path'] = config
    
    # Initialize configuration system
    try:
        config_loader = ConfigLoader()
        
        # Handle configuration-related commands first
        if show_config_locations:
            config_loader.show_config_locations()
            return
        
        if generate_config:
            from .config.templates import generate_config_template
            config_content = generate_config_template()
            console.print(config_content)
            return
        
        if validate_config:
            if config_loader.validate_config_file(config or "auto-discovered"):
                console.print("[green]✅ Configuration is valid![/green]")
            else:
                ctx.exit(1)
            return
            
        # Load configuration
        app_config = config_loader.load_config(config)
        ctx.obj['config'] = app_config
        ctx.obj['config_loader'] = config_loader
        
        if list_profiles:
            display_available_profiles(app_config)
            return
        
        # Set Rich theme from config or CLI override
        effective_theme = theme if theme != "auto" else app_config.rich.theme
        try:
            set_theme(effective_theme)
        except Exception:
            set_theme('auto')
    
    except ConfigError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        ctx.exit(1)
    
    # Apply profile configuration if specified
    if profile:
        try:
            profile_config = config_loader.get_profile(profile, app_config)
            ctx.obj['profile'] = profile_config
            console.print(f"[dim]Using profile: {profile} - {profile_config.description or 'No description'}[/dim]")
        except ConfigError as e:
            console.print(f"[red]Profile Error:[/red] {e}")
            ctx.exit(1)
    
    # Determine which command to execute based on provided options
    command_provided = False
    
    if scan_directories:
        command_provided = True
        execute_scan_with_config(ctx, scan_directories, pattern, not no_recursive, 
                               output_format or 'table')
    
    if edit_directories:
        command_provided = True
        execute_edit_with_config(ctx, edit_directories, field_updates, pattern, 
                               edit_output_format, backup, dry_run, max_files)
    
    if detect_file:
        command_provided = True
        if not os.path.exists(detect_file):
            console.print(f"[red]Error:[/red] File not found: {detect_file}")
            ctx.exit(1)
        detect_command(ctx, detect_file, output_format or 'table')
    
    if load_file:
        command_provided = True
        if not os.path.exists(load_file):
            console.print(f"[red]Error:[/red] File not found: {load_file}")
            ctx.exit(1)
        load_command(ctx, load_file, output_format or 'table', fields)
    
    # If no command flags provided, launch interactive mode
    if not command_provided:
        launch_interactive_mode(ctx)


def launch_interactive_mode(ctx: click.Context):
    """
    Launch the interactive TUI mode.
    
    Args:
        ctx: Click context with configuration
    """
    if not INTERACTIVE_AVAILABLE:
        console.print("[red]Error:[/red] Interactive mode requires additional dependencies.")
        console.print("Install with: [cyan]uv add textual[/cyan]")
        console.print("Falling back to CLI mode. Use --help for available commands.")
        return
    
    try:
        # Load configuration if specified
        config_data = None
        if ctx.obj.get('config_path'):
            config_loader = ConfigLoader()
            config_data = config_loader.load_config(ctx.obj['config_path'])
        
        # Create and run the interactive app
        app = NFOEditorApp(config=config_data)
        app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interactive mode cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error launching interactive mode:[/red] {e}")
        console.print("Use --help for CLI mode options.")


def display_available_profiles(config: NFOEditorConfig) -> None:
    """
    Display available configuration profiles.
    
    Args:
        config: Configuration containing profiles
    """
    if not config.profiles:
        console.print("[yellow]No profiles configured.[/yellow]")
        console.print("Add profiles to your configuration file to create reusable workflows.")
        return
    
    from rich.table import Table
    
    table = Table(title="📋 Available Profiles")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Directories", style="dim")
    table.add_column("Patterns", style="dim")
    
    for profile in config.profiles:
        directories_str = ", ".join(profile.directories)
        patterns_str = ", ".join(profile.patterns) if profile.patterns else "default"
        
        table.add_row(
            profile.name,
            profile.description or "[dim]No description[/dim]",
            directories_str,
            patterns_str
        )
    
    console.print(table)
    console.print()
    console.print("[dim]Usage: nfo-editor --profile <name> [other options][/dim]")


def execute_scan_with_config(ctx: click.Context, directories: Tuple[str, ...],
                           pattern: Optional[str], recursive: bool, output_format: str):
    """Execute scan command with configuration support."""
    app_config = ctx.obj.get('config')
    profile_config = ctx.obj.get('profile')
    
    # Use profile settings if available
    if profile_config and profile_config.scan_options:
        scan_opts = profile_config.scan_options
        pattern = pattern or (scan_opts.pattern if scan_opts else None)
        if scan_opts and hasattr(scan_opts, 'recursive'):
            recursive = scan_opts.recursive
    elif app_config:
        # Use global scan settings
        pattern = pattern or app_config.scan.pattern
        recursive = recursive if 'no_recursive' in sys.argv else app_config.scan.recursive
    
    # Resolve directory references
    resolved_dirs = resolve_directory_references(directories, app_config, profile_config)
    
    from .commands.scan import scan_command
    scan_command(ctx, resolved_dirs, pattern, recursive, output_format)


def execute_edit_with_config(ctx: click.Context, directories: Tuple[str, ...],
                           field_updates: Tuple[str, ...], pattern: Optional[str],
                           edit_output_format: Optional[str], backup: bool, 
                           dry_run: bool, max_files: Optional[int]):
    """Execute edit command with configuration support."""
    app_config = ctx.obj.get('config')
    profile_config = ctx.obj.get('profile')
    
    # Merge field updates from profile and CLI
    merged_updates = {}
    
    if profile_config and profile_config.field_updates:
        merged_updates.update(profile_config.field_updates)
    
    # Parse CLI field updates
    for update in field_updates or []:
        if '=' in update:
            field, value = update.split('=', 1)
            # Convert string values to appropriate types
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').replace('-', '').isdigit():
                try:
                    value = float(value)
                except ValueError:
                    pass
            merged_updates[field.strip()] = value
    
    # Use profile or config settings for other options
    if profile_config and profile_config.edit_options:
        edit_opts = profile_config.edit_options
        backup = backup if '--backup' in sys.argv or '--no-backup' in sys.argv else edit_opts.backup
        max_files = max_files or edit_opts.max_files
    elif app_config:
        edit_opts = app_config.edit
        backup = backup if '--backup' in sys.argv or '--no-backup' in sys.argv else edit_opts.backup
        max_files = max_files or edit_opts.max_files
        dry_run = dry_run or edit_opts.dry_run_default
    
    # Use profile patterns if specified
    if profile_config and profile_config.patterns:
        pattern = pattern or profile_config.patterns[0]  # Use first pattern
    
    # Resolve directory references
    resolved_dirs = resolve_directory_references(directories, app_config, profile_config)
    
    from .commands.edit import edit_command
    edit_command(ctx, resolved_dirs, tuple(f"{k}={v}" for k, v in merged_updates.items()),
                pattern, edit_output_format, backup, dry_run, max_files)


def resolve_directory_references(directories: Tuple[str, ...], 
                                app_config: Optional[NFOEditorConfig],
                                profile_config=None) -> Tuple[str, ...]:
    """
    Resolve directory names to actual paths using configuration.
    
    Args:
        directories: Directory names or paths from CLI
        app_config: Application configuration
        profile_config: Profile configuration (if any)
        
    Returns:
        Resolved directory paths
    """
    resolved = []
    
    # If using profile, use profile directories if none specified
    if not directories and profile_config:
        directories = tuple(profile_config.directories)
    
    for directory in directories:
        # If it's an absolute path, use as-is
        if os.path.isabs(directory):
            resolved.append(directory)
            continue
            
        # Try to resolve as directory name from config
        if app_config:
            dir_config = app_config.directories
            if directory == 'movies' and dir_config.movies:
                resolved.append(dir_config.movies)
            elif directory == 'tv' and dir_config.tv:
                resolved.append(dir_config.tv) 
            elif directory == 'music' and dir_config.music:
                resolved.append(dir_config.music)
            elif directory in dir_config.custom_dirs:
                resolved.append(dir_config.custom_dirs[directory])
            else:
                # Use as-is if not found in config
                resolved.append(directory)
        else:
            resolved.append(directory)
    
    return tuple(resolved)





def main():
    """
    Main entry point for the NFO Editor CLI application.
    
    This function serves as the entry point defined in pyproject.toml.
    It handles the interactive-first behavior and CLI argument processing.
    """
    import os
    
    # Handle legacy argument patterns for backward compatibility
    if len(sys.argv) > 1:
        # Convert legacy commands to new flag-based approach
        legacy_conversions = {
            'scan': '--scan',
            'edit': '--edit', 
            'detect': '--detect',
            'load': '--load'
        }
        
        if sys.argv[1] in legacy_conversions:
            # Convert legacy command to flag-based approach
            sys.argv[1] = legacy_conversions[sys.argv[1]]
            console.print(f"[yellow]Note:[/yellow] Legacy command format detected. "
                         f"Consider using '{sys.argv[1]}' flag format.")
    
    # Launch the Click CLI application
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        if os.environ.get('NFO_EDITOR_DEBUG'):
            raise
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
