"""
NFO Editor Library

A Python library for parsing and editing .nfo files in various formats including
XML, JSON, and plain text key-value pairs.

This library provides a comprehensive solution for working with NFO (information)
files commonly used for media metadata. It supports automatic format detection,
batch editing operations, and preserves data integrity while providing flexible
output options.

Key Features:
- Support for XML, JSON, and plain text NFO formats
- Automatic format detection and conversion
- Batch operations across multiple directories
- Backup creation and safe editing
- Extensible parser and writer architecture
- Comprehensive error handling and logging

Author: NFO Editor Team
Version: 0.1.0
"""

from typing import List, Optional, Union, Dict, Any
from pathlib import Path

# Core functionality
from .core.editor import NFOEditor, EditResult, BatchEditResult
from .core.scanner import NFOScanner, ScanResult
from .core.detector import NFOFormatDetector, FormatDetectionResult, NFOFormat

# Data structures
from .parsers.base import NFOData

# Parser classes (for advanced usage)
from .parsers.xml_parser import XMLNFOParser
from .parsers.json_parser import JSONNFOParser  
from .parsers.text_parser import TextNFOParser

# Writer classes (for advanced usage)
from .writers.xml_writer import XMLNFOWriter
from .writers.json_writer import JSONNFOWriter
from .writers.text_writer import TextNFOWriter

# Exception classes
from .utils.exceptions import (
    NFOError,
    NFOParseError,
    NFOFieldError,
    NFOAccessError,
    NFOFormatError,
)

__version__ = "0.1.0"
__author__ = "NFO Editor Team"
__email__ = "nfo@example.com"

# Public API exports
__all__ = [
    # Core classes
    "NFOEditor",
    "NFOScanner", 
    "NFOFormatDetector",
    "NFOData",
    
    # Result classes
    "EditResult",
    "BatchEditResult",
    "ScanResult",
    "FormatDetectionResult",
    
    # Enums
    "NFOFormat",
    
    # Parser classes (advanced)
    "XMLNFOParser",
    "JSONNFOParser",
    "TextNFOParser",
    
    # Writer classes (advanced)
    "XMLNFOWriter", 
    "JSONNFOWriter",
    "TextNFOWriter",
    
    # Exceptions
    "NFOError",
    "NFOParseError",
    "NFOFieldError",
    "NFOAccessError",
    "NFOFormatError",
    
    # Convenience functions
    "edit_nfo_files",
    "scan_nfo_files",
    "detect_nfo_format",
    "load_nfo_file",
]


def edit_nfo_files(
    directories: Union[str, Path, List[Union[str, Path]]],
    field_updates: Dict[str, Any],
    backup: bool = True,
    dry_run: bool = False,
    file_pattern: Optional[str] = None,
    output_format: Optional[str] = None,
    max_files: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to edit .nfo files in specified directories.
    
    This is the main entry point for simple batch editing operations.
    For more advanced usage, create an NFOEditor instance directly.
    
    Args:
        directories: Single directory or list of directories to scan
        field_updates: Dictionary of field names and values to update
        backup: Whether to create backup files before editing
        dry_run: If True, only preview changes without applying them
        file_pattern: Optional glob pattern to filter files (e.g., "*movie*.nfo")
        output_format: Optional format for output files ("xml", "json", "text")
        max_files: Optional maximum number of files to process
    
    Returns:
        Dictionary with results including files processed and any errors
    
    Example:
        >>> # Basic usage
        >>> results = edit_nfo_files(
        ...     directories=['/media/movies'],
        ...     field_updates={'genre': 'Action', 'year': '2024'},
        ...     backup=True
        ... )
        
        >>> # Preview changes without applying
        >>> preview = edit_nfo_files(
        ...     directories=['/media/movies'],
        ...     field_updates={'rating': '8.5'},
        ...     dry_run=True
        ... )
        
        >>> # Filter specific files and convert format
        >>> results = edit_nfo_files(
        ...     directories=['/media/tv'],
        ...     field_updates={'studio': 'Netflix'},
        ...     file_pattern="*episode*.nfo",
        ...     output_format="json"
        ... )
    """
    editor = NFOEditor(directories=directories, create_backups=backup)
    
    if dry_run:
        return editor.preview_changes(
            field_updates, 
            file_pattern=file_pattern,
            max_files=max_files or 10
        )
    else:
        batch_result = editor.batch_edit(
            field_updates,
            file_pattern=file_pattern,
            output_format=output_format,
            max_files=max_files
        )
        
        # Convert BatchEditResult to dictionary for convenience
        return {
            'success': batch_result.successful_edits > 0,
            'total_files': batch_result.total_files,
            'successful_edits': batch_result.successful_edits,
            'failed_edits': batch_result.failed_edits,
            'execution_time_seconds': batch_result.execution_time_seconds,
            'errors': batch_result.errors,
            'results': [
                {
                    'file_path': str(result.file_path),
                    'success': result.success,
                    'fields_updated': result.fields_updated,
                    'original_format': result.original_format,
                    'output_format': result.output_format,
                    'backup_path': str(result.backup_path) if result.backup_path else None,
                    'errors': result.errors,
                    'warnings': result.warnings
                }
                for result in batch_result.results
            ]
        }


def scan_nfo_files(
    directories: Union[str, Path, List[Union[str, Path]]],
    pattern: Optional[str] = None,
    recursive: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to scan directories for .nfo files.
    
    Args:
        directories: Single directory or list of directories to scan
        pattern: Optional glob pattern to filter files
        recursive: Whether to scan subdirectories recursively
    
    Returns:
        Dictionary with scan results and statistics
    
    Example:
        >>> # Scan for all NFO files
        >>> result = scan_nfo_files(['/media/movies', '/media/tv'])
        
        >>> # Scan for specific pattern
        >>> result = scan_nfo_files('/media/music', pattern="*album*.nfo")
    """
    scanner = NFOScanner()
    
    if not recursive:
        scanner.max_depth = 0
    
    scan_result = scanner.scan_directories(directories, pattern=pattern)
    
    return {
        'nfo_files': [str(path) for path in scan_result.nfo_files],
        'total_files_scanned': scan_result.total_files_scanned,
        'directories_scanned': scan_result.directories_scanned,
        'scan_time_seconds': scan_result.scan_time_seconds,
        'errors': scan_result.errors,
        'filter_pattern': scan_result.filter_pattern
    }


def detect_nfo_format(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to detect the format of an NFO file.
    
    Args:
        file_path: Path to the NFO file to analyze
    
    Returns:
        Dictionary with format detection results
    
    Example:
        >>> result = detect_nfo_format('/media/movie.nfo')
        >>> print(f"Format: {result['format']}, Confidence: {result['confidence']}")
    """
    detector = NFOFormatDetector()
    detection_result = detector.detect_format(file_path)
    
    return {
        'format': detection_result.format_type.value,
        'confidence': detection_result.confidence,
        'details': detection_result.details,
        'fallback_formats': [fmt.value for fmt in detection_result.fallback_formats],
        'encoding': detection_result.encoding
    }


def load_nfo_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to load and parse a single NFO file.
    
    Args:
        file_path: Path to the NFO file to load
    
    Returns:
        Dictionary with parsed file data and metadata
    
    Example:
        >>> data = load_nfo_file('/media/movie.nfo')
        >>> title = data['fields'].get('title', 'Unknown')
        >>> print(f"Movie: {title}")
    """
    editor = NFOEditor()
    nfo_data = editor.load_file(file_path)
    
    return {
        'file_path': str(nfo_data.file_path),
        'format_type': nfo_data.format_type,
        'encoding': nfo_data.encoding,
        'is_modified': nfo_data.is_modified,
        'fields': nfo_data.data,
        'all_fields_flat': nfo_data.get_all_fields(),
        'metadata': nfo_data.metadata
    }
