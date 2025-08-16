"""
Directory scanning functionality for finding NFO files.

This module provides classes and functions for recursively scanning directories
to locate .nfo files that can be processed by the NFO editor library.

Author: NFO Editor Team
"""

import os
import fnmatch
from typing import List, Union, Iterator, Optional, Set, Callable
from pathlib import Path
from dataclasses import dataclass, field

from ..utils.exceptions import NFOAccessError


@dataclass
class ScanResult:
    """
    Result of a directory scan operation.
    
    Attributes:
        nfo_files (List[Path]): List of found .nfo files
        total_files_scanned (int): Total number of files examined
        directories_scanned (int): Number of directories examined
        errors (List[str]): List of error messages encountered during scan
        scan_time_seconds (float): Time taken to complete the scan
        filter_pattern (Optional[str]): Pattern used to filter files (if any)
    """
    nfo_files: List[Path] = field(default_factory=list)
    total_files_scanned: int = 0
    directories_scanned: int = 0
    errors: List[str] = field(default_factory=list)
    scan_time_seconds: float = 0.0
    filter_pattern: Optional[str] = None


class NFOScanner:
    """
    Scanner for finding .nfo files in directory structures.
    
    This class provides methods to recursively scan directories and locate
    .nfo files based on various criteria such as file extensions, patterns,
    and custom filters.
    
    Attributes:
        default_extensions (Set[str]): Default file extensions to scan for
        case_sensitive (bool): Whether filename matching should be case-sensitive
        follow_symlinks (bool): Whether to follow symbolic links during scanning
        max_depth (Optional[int]): Maximum directory depth to scan (None for unlimited)
        exclude_patterns (Set[str]): Patterns of files/directories to exclude
    """
    
    def __init__(
        self,
        extensions: Optional[Set[str]] = None,
        case_sensitive: bool = False,
        follow_symlinks: bool = True,
        max_depth: Optional[int] = None,
        exclude_patterns: Optional[Set[str]] = None
    ) -> None:
        """
        Initialize NFO scanner.
        
        Args:
            extensions: File extensions to scan for (defaults to .nfo variants)
            case_sensitive: Whether filename matching should be case-sensitive
            follow_symlinks: Whether to follow symbolic links during scanning
            max_depth: Maximum directory depth to scan (None for unlimited)
            exclude_patterns: Patterns of files/directories to exclude
        """
        self.default_extensions = extensions or {
            '.nfo', '.NFO', '.xml', '.XML', '.json', '.JSON',
            '.info', '.INFO', '.meta', '.META'
        }
        self.case_sensitive = case_sensitive
        self.follow_symlinks = follow_symlinks
        self.max_depth = max_depth
        self.exclude_patterns = exclude_patterns or {
            '.*',           # Hidden files
            '__pycache__',  # Python cache
            '*.tmp',        # Temporary files
            '*.bak',        # Backup files
            '*.swp',        # Swap files
            'node_modules', # Node.js modules
            '.git',         # Git directory
            '.svn',         # SVN directory
        }
    
    def scan_directories(
        self, 
        directories: Union[str, Path, List[Union[str, Path]]], 
        pattern: Optional[str] = None,
        custom_filter: Optional[Callable[[Path], bool]] = None
    ) -> ScanResult:
        """
        Scan one or more directories for .nfo files.
        
        Args:
            directories: Single directory path or list of directory paths to scan
            pattern: Optional glob pattern to filter files (e.g., "*movie*.nfo")
            custom_filter: Optional custom filter function for additional filtering
            
        Returns:
            ScanResult object containing scan results and statistics
            
        Raises:
            NFOAccessError: If directories cannot be accessed
        """
        import time
        
        start_time = time.time()
        result = ScanResult(filter_pattern=pattern)
        
        # Normalize input to list of Path objects
        if isinstance(directories, (str, Path)):
            directories = [directories]
        
        dir_paths = [Path(d) for d in directories]
        
        # Validate directories exist
        for dir_path in dir_paths:
            if not dir_path.exists():
                error_msg = f"Directory does not exist: {dir_path}"
                result.errors.append(error_msg)
                continue
            
            if not dir_path.is_dir():
                error_msg = f"Path is not a directory: {dir_path}"
                result.errors.append(error_msg)
                continue
            
            # Scan this directory
            try:
                self._scan_single_directory(
                    dir_path, result, pattern, custom_filter, depth=0
                )
            except Exception as e:
                error_msg = f"Error scanning {dir_path}: {str(e)}"
                result.errors.append(error_msg)
        
        result.scan_time_seconds = time.time() - start_time
        return result
    
    def _scan_single_directory(
        self,
        directory: Path,
        result: ScanResult,
        pattern: Optional[str],
        custom_filter: Optional[Callable[[Path], bool]],
        depth: int
    ) -> None:
        """
        Recursively scan a single directory.
        
        Args:
            directory: Directory to scan
            result: ScanResult object to update
            pattern: Optional glob pattern to filter files
            custom_filter: Optional custom filter function
            depth: Current scanning depth
        """
        try:
            # Check depth limit
            if self.max_depth is not None and depth > self.max_depth:
                return
            
            result.directories_scanned += 1
            
            # Iterate through directory contents
            for entry in directory.iterdir():
                try:
                    # Skip if matches exclude patterns
                    if self._should_exclude(entry):
                        continue
                    
                    # Handle symbolic links
                    if entry.is_symlink() and not self.follow_symlinks:
                        continue
                    
                    if entry.is_file():
                        result.total_files_scanned += 1
                        
                        # Check if this is an NFO file
                        if self._is_nfo_file(entry, pattern, custom_filter):
                            result.nfo_files.append(entry)
                    
                    elif entry.is_dir():
                        # Recursively scan subdirectory
                        self._scan_single_directory(
                            entry, result, pattern, custom_filter, depth + 1
                        )
                
                except PermissionError:
                    result.errors.append(f"Permission denied: {entry}")
                except Exception as e:
                    result.errors.append(f"Error processing {entry}: {str(e)}")
        
        except PermissionError:
            result.errors.append(f"Permission denied accessing directory: {directory}")
        except Exception as e:
            result.errors.append(f"Error scanning directory {directory}: {str(e)}")
    
    def _is_nfo_file(
        self, 
        file_path: Path, 
        pattern: Optional[str],
        custom_filter: Optional[Callable[[Path], bool]]
    ) -> bool:
        """
        Check if a file should be considered an NFO file.
        
        Args:
            file_path: Path to the file to check
            pattern: Optional glob pattern to match
            custom_filter: Optional custom filter function
            
        Returns:
            True if the file should be processed as an NFO file
        """
        # Check file extension
        if not self._has_nfo_extension(file_path):
            return False
        
        # Apply glob pattern if specified
        if pattern is not None:
            if not fnmatch.fnmatch(
                file_path.name, 
                pattern, 
                fnmatch.FNM_CASEFOLD if not self.case_sensitive else 0
            ):
                return False
        
        # Apply custom filter if specified
        if custom_filter is not None:
            try:
                if not custom_filter(file_path):
                    return False
            except Exception:
                # If custom filter fails, skip this file
                return False
        
        return True
    
    def _has_nfo_extension(self, file_path: Path) -> bool:
        """
        Check if a file has an NFO-related extension.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file has a relevant extension
        """
        extension = file_path.suffix
        
        if self.case_sensitive:
            return extension in self.default_extensions
        else:
            return extension.lower() in {ext.lower() for ext in self.default_extensions}
    
    def _should_exclude(self, path: Path) -> bool:
        """
        Check if a path should be excluded based on exclude patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be excluded
        """
        name = path.name
        
        for pattern in self.exclude_patterns:
            # Handle glob patterns
            if fnmatch.fnmatch(
                name, 
                pattern, 
                fnmatch.FNM_CASEFOLD if not self.case_sensitive else 0
            ):
                return True
        
        return False
    
    def find_files_by_pattern(
        self, 
        directories: Union[str, Path, List[Union[str, Path]]], 
        pattern: str
    ) -> List[Path]:
        """
        Find NFO files matching a specific pattern.
        
        Args:
            directories: Directory or directories to search
            pattern: Glob pattern to match (e.g., "*movie*.nfo")
            
        Returns:
            List of matching file paths
        """
        result = self.scan_directories(directories, pattern=pattern)
        return result.nfo_files
    
    def find_files_with_filter(
        self,
        directories: Union[str, Path, List[Union[str, Path]]],
        custom_filter: Callable[[Path], bool]
    ) -> List[Path]:
        """
        Find NFO files using a custom filter function.
        
        Args:
            directories: Directory or directories to search
            custom_filter: Function that returns True for files to include
            
        Returns:
            List of matching file paths
        """
        result = self.scan_directories(directories, custom_filter=custom_filter)
        return result.nfo_files
    
    def get_scan_statistics(
        self, 
        directories: Union[str, Path, List[Union[str, Path]]]
    ) -> dict:
        """
        Get statistics about files in directories without returning file list.
        
        Args:
            directories: Directory or directories to analyze
            
        Returns:
            Dictionary with scan statistics
        """
        result = self.scan_directories(directories)
        
        return {
            'nfo_files_found': len(result.nfo_files),
            'total_files_scanned': result.total_files_scanned,
            'directories_scanned': result.directories_scanned,
            'errors_encountered': len(result.errors),
            'scan_time_seconds': result.scan_time_seconds,
            'average_files_per_directory': (
                result.total_files_scanned / result.directories_scanned 
                if result.directories_scanned > 0 else 0
            )
        }
