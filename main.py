"""
Command-line interface for NFO Editor.

This module provides a command-line interface for the NFO Editor library,
allowing users to edit NFO files from the terminal with various options
and batch operations.

Author: NFO Editor Team
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from nfo_editor import (
    edit_nfo_files, scan_nfo_files, detect_nfo_format, load_nfo_file,
    NFOEditor, NFOError
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='nfo-editor',
        description='Edit and manage NFO files across various formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Edit files in a directory
  nfo-editor edit /media/movies --set title="New Movie Title" year=2024
  
  # Preview changes without applying
  nfo-editor edit /media/movies --set genre=Action --dry-run
  
  # Scan directories for NFO files
  nfo-editor scan /media/movies /media/tv --pattern "*movie*.nfo"
  
  # Detect format of a specific file
  nfo-editor detect /media/movie.nfo
  
  # Load and display file contents
  nfo-editor load /media/movie.nfo --format json
  
  # Convert files to different format
  nfo-editor edit /media/movies --output-format json --backup
        """
    )
    
    # Global options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Edit command
    edit_parser = subparsers.add_parser(
        'edit',
        help='Edit NFO files'
    )
    edit_parser.add_argument(
        'directories',
        nargs='+',
        help='Directories to scan for NFO files'
    )
    edit_parser.add_argument(
        '--set',
        action='append',
        dest='field_updates',
        metavar='FIELD=VALUE',
        help='Set field values (can be used multiple times)'
    )
    edit_parser.add_argument(
        '--pattern',
        help='Glob pattern to filter files (e.g., "*movie*.nfo")'
    )
    edit_parser.add_argument(
        '--output-format',
        choices=['xml', 'json', 'text'],
        help='Output format for edited files'
    )
    edit_parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backup files (default: enabled)'
    )
    edit_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Disable backup file creation'
    )
    edit_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    edit_parser.add_argument(
        '--max-files',
        type=int,
        help='Maximum number of files to process'
    )
    
    # Scan command
    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan directories for NFO files'
    )
    scan_parser.add_argument(
        'directories',
        nargs='+',
        help='Directories to scan'
    )
    scan_parser.add_argument(
        '--pattern',
        help='Glob pattern to filter files'
    )
    scan_parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Disable recursive directory scanning'
    )
    scan_parser.add_argument(
        '--format',
        choices=['table', 'json', 'list'],
        default='table',
        help='Output format for results'
    )
    
    # Detect command  
    detect_parser = subparsers.add_parser(
        'detect',
        help='Detect NFO file format'
    )
    detect_parser.add_argument(
        'file',
        help='NFO file to analyze'
    )
    detect_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format for results'
    )
    
    # Load command
    load_parser = subparsers.add_parser(
        'load',
        help='Load and display NFO file contents'
    )
    load_parser.add_argument(
        'file',
        help='NFO file to load'
    )
    load_parser.add_argument(
        '--format',
        choices=['json', 'yaml', 'table'],
        default='table',
        help='Output format for file contents'
    )
    load_parser.add_argument(
        '--fields',
        nargs='*',
        help='Specific fields to display (default: all)'
    )
    
    return parser


def parse_field_updates(field_updates: List[str]) -> Dict[str, Any]:
    """
    Parse field update strings into a dictionary.
    
    Args:
        field_updates: List of "field=value" strings
        
    Returns:
        Dictionary of field updates
    """
    updates = {}
    
    for update in field_updates or []:
        if '=' not in update:
            print(f"Error: Invalid field update format: {update}", file=sys.stderr)
            print("Use format: field=value", file=sys.stderr)
            sys.exit(1)
        
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


def command_edit(args: argparse.Namespace) -> None:
    """
    Handle the edit command.
    
    Args:
        args: Parsed command-line arguments
    """
    # Parse field updates
    field_updates = parse_field_updates(args.field_updates)
    
    if not field_updates:
        print("Error: No field updates specified. Use --set field=value", file=sys.stderr)
        sys.exit(1)
    
    # Determine backup setting
    backup = args.backup and not args.no_backup
    
    try:
        # Execute edit operation
        result = edit_nfo_files(
            directories=args.directories,
            field_updates=field_updates,
            backup=backup,
            dry_run=args.dry_run,
            file_pattern=args.pattern,
            output_format=args.output_format,
            max_files=args.max_files
        )
        
        # Display results
        if args.dry_run:
            print("Preview of changes (dry run):")
            print(f"Files that would be processed: {result.get('files_previewed', 0)}")
            
            for file_preview in result.get('file_previews', []):
                if 'error' in file_preview:
                    print(f"  ❌ {file_preview['file_path']}: {file_preview['error']}")
                else:
                    print(f"  📄 {file_preview['file_path']} ({file_preview['format']})")
                    for field, change in file_preview['field_changes'].items():
                        if change['will_change']:
                            print(f"    {field}: {change['current']} → {change['new']}")
        else:
            print("Edit operation completed:")
            print(f"Total files: {result['total_files']}")
            print(f"Successful edits: {result['successful_edits']}")
            print(f"Failed edits: {result['failed_edits']}")
            print(f"Execution time: {result['execution_time_seconds']:.2f} seconds")
            
            if result['errors']:
                print("\nErrors:")
                for error in result['errors']:
                    print(f"  ❌ {error}")
            
            # Show individual file results if verbose or if there were issues
            if args.verbose or result['failed_edits'] > 0:
                print("\nFile results:")
                for file_result in result['results']:
                    status = "✅" if file_result['success'] else "❌"
                    print(f"  {status} {file_result['file_path']}")
                    
                    if file_result['errors']:
                        for error in file_result['errors']:
                            print(f"    Error: {error}")
                    
                    if file_result['warnings']:
                        for warning in file_result['warnings']:
                            print(f"    Warning: {warning}")
    
    except NFOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def command_scan(args: argparse.Namespace) -> None:
    """
    Handle the scan command.
    
    Args:
        args: Parsed command-line arguments
    """
    try:
        result = scan_nfo_files(
            directories=args.directories,
            pattern=args.pattern,
            recursive=not args.no_recursive
        )
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        elif args.format == 'list':
            for file_path in result['nfo_files']:
                print(file_path)
        else:  # table format
            print(f"Scan Results:")
            print(f"NFO files found: {len(result['nfo_files'])}")
            print(f"Directories scanned: {result['directories_scanned']}")
            print(f"Total files scanned: {result['total_files_scanned']}")
            print(f"Scan time: {result['scan_time_seconds']:.2f} seconds")
            
            if result['errors']:
                print(f"\nErrors ({len(result['errors'])}):")
                for error in result['errors']:
                    print(f"  ❌ {error}")
            
            if result['nfo_files'] and not args.quiet:
                print(f"\nFound NFO files:")
                for file_path in result['nfo_files']:
                    print(f"  📄 {file_path}")
    
    except NFOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def command_detect(args: argparse.Namespace) -> None:
    """
    Handle the detect command.
    
    Args:
        args: Parsed command-line arguments
    """
    try:
        result = detect_nfo_format(args.file)
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:  # table format
            print(f"Format Detection Results for: {args.file}")
            print(f"Detected format: {result['format']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Encoding: {result['encoding']}")
            
            if result['fallback_formats']:
                print(f"Fallback formats: {', '.join(result['fallback_formats'])}")
            
            if result['details'] and args.verbose:
                print("\nDetection details:")
                for key, value in result['details'].items():
                    print(f"  {key}: {value}")
    
    except NFOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def command_load(args: argparse.Namespace) -> None:
    """
    Handle the load command.
    
    Args:
        args: Parsed command-line arguments
    """
    try:
        result = load_nfo_file(args.file)
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:  # table format
            print(f"NFO File Contents: {args.file}")
            print(f"Format: {result['format_type']}")
            print(f"Encoding: {result['encoding']}")
            print(f"Modified: {result['is_modified']}")
            
            # Display fields
            fields_to_show = result['all_fields_flat'] if not args.fields else {
                k: v for k, v in result['all_fields_flat'].items() 
                if any(field.lower() in k.lower() for field in args.fields)
            }
            
            if fields_to_show:
                print("\nFields:")
                for field, value in fields_to_show.items():
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:97] + "..."
                    print(f"  {field}: {value}")
            else:
                print("\nNo fields found matching criteria.")
    
    except NFOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the CLI application.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle no command specified
    if not args.command:
        parser.print_help()
        return
    
    # Set up global options
    if args.quiet:
        # Suppress all non-error output by redirecting stdout to devnull
        import os
        sys.stdout = open(os.devnull, 'w')
    
    # Dispatch to command handlers
    if args.command == 'edit':
        command_edit(args)
    elif args.command == 'scan':
        command_scan(args)
    elif args.command == 'detect':
        command_detect(args)
    elif args.command == 'load':
        command_load(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
