"""
Main NFO editor functionality.

This module provides the primary NFOEditor class that coordinates all the
components of the library including scanning, parsing, editing, and writing
NFO files across different formats.

Author: NFO Editor Team
"""

from typing import Union, List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, field

from .scanner import NFOScanner, ScanResult
from .detector import NFOFormatDetector, FormatDetectionResult, NFOFormat
from ..parsers.base import BaseNFOParser, NFOData
from ..parsers.xml_parser import XMLNFOParser
from ..parsers.json_parser import JSONNFOParser
from ..parsers.text_parser import TextNFOParser
from ..writers.base import BaseNFOWriter
from ..writers.xml_writer import XMLNFOWriter
from ..writers.json_writer import JSONNFOWriter
from ..writers.text_writer import TextNFOWriter
from ..utils.exceptions import (
    NFOError, NFOParseError, NFOFieldError, NFOAccessError, NFOFormatError
)


@dataclass
class EditResult:
    """
    Result of an edit operation.
    
    Attributes:
        file_path (Path): Path to the edited file
        success (bool): Whether the edit was successful
        fields_updated (Dict[str, Any]): Fields that were updated
        original_format (str): Original file format
        output_format (str): Output file format
        backup_path (Optional[Path]): Path to backup file (if created)
        errors (List[str]): Any errors encountered
        warnings (List[str]): Any warnings generated
    """
    file_path: Path
    success: bool
    fields_updated: Dict[str, Any] = field(default_factory=dict)
    original_format: str = "unknown"
    output_format: str = "unknown"
    backup_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class BatchEditResult:
    """
    Result of a batch edit operation.
    
    Attributes:
        total_files (int): Total number of files processed
        successful_edits (int): Number of successful edits
        failed_edits (int): Number of failed edits
        results (List[EditResult]): Individual edit results
        errors (List[str]): Global errors encountered
        execution_time_seconds (float): Total execution time
    """
    total_files: int
    successful_edits: int
    failed_edits: int
    results: List[EditResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0


class NFOEditor:
    """
    Main NFO file editor class.
    
    This class provides a high-level interface for editing NFO files across
    different formats and directories. It coordinates scanning, parsing, editing,
    and writing operations while handling errors and providing detailed feedback.
    
    Attributes:
        directories (List[Path]): Directories to scan for NFO files
        create_backups (bool): Whether to create backup files before editing
        auto_detect_format (bool): Whether to auto-detect file formats
        preserve_format (bool): Whether to preserve original file format
        default_output_format (str): Default format for new files
    """
    
    def __init__(
        self,
        directories: Optional[Union[str, Path, List[Union[str, Path]]]] = None,
        create_backups: bool = True,
        auto_detect_format: bool = True,
        preserve_format: bool = True,
        default_output_format: str = "xml"
    ) -> None:
        """
        Initialize NFO Editor.
        
        Args:
            directories: Directory or directories to scan
            create_backups: Whether to create backup files before editing
            auto_detect_format: Whether to auto-detect file formats
            preserve_format: Whether to preserve original file format
            default_output_format: Default format for output files
        """
        # Store configuration
        self.create_backups = create_backups
        self.auto_detect_format = auto_detect_format
        self.preserve_format = preserve_format
        self.default_output_format = default_output_format
        
        # Initialize directories
        self.directories: List[Path] = []
        if directories is not None:
            self.add_directories(directories)
        
        # Initialize components
        self.scanner = NFOScanner()
        self.detector = NFOFormatDetector()
        
        # Initialize parsers
        self.parsers: Dict[str, BaseNFOParser] = {
            'xml': XMLNFOParser(),
            'json': JSONNFOParser(),
            'text': TextNFOParser()
        }
        
        # Initialize writers  
        self.writers: Dict[str, BaseNFOWriter] = {
            'xml': XMLNFOWriter(),
            'json': JSONNFOWriter(),
            'text': TextNFOWriter()
        }
        
        # Cache for parsed files
        self._file_cache: Dict[str, NFOData] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def add_directories(self, directories: Union[str, Path, List[Union[str, Path]]]) -> None:
        """
        Add directories to scan.
        
        Args:
            directories: Directory or list of directories to add
        """
        if isinstance(directories, (str, Path)):
            directories = [directories]
        
        for directory in directories:
            path = Path(directory)
            if path.exists() and path.is_dir():
                self.directories.append(path)
            else:
                self.logger.warning(f"Directory does not exist or is not a directory: {path}")
    
    def scan_files(self, pattern: Optional[str] = None) -> ScanResult:
        """
        Scan directories for NFO files.
        
        Args:
            pattern: Optional glob pattern to filter files
            
        Returns:
            ScanResult object with found files and statistics
        """
        if not self.directories:
            raise NFOError("No directories specified for scanning")
        
        return self.scanner.scan_directories(self.directories, pattern=pattern)
    
    def load_file(self, file_path: Union[str, Path]) -> NFOData:
        """
        Load and parse a single NFO file.
        
        Args:
            file_path: Path to the NFO file
            
        Returns:
            NFOData object containing parsed file data
            
        Raises:
            NFOParseError: If file cannot be parsed
            NFOAccessError: If file cannot be read
            NFOFormatError: If format is not supported
        """
        file_path = Path(file_path)
        file_key = str(file_path)
        
        # Check cache first
        if file_key in self._file_cache:
            return self._file_cache[file_key]
        
        # Detect format if auto-detection is enabled
        if self.auto_detect_format:
            detection_result = self.detector.detect_format(file_path)
            format_type = detection_result.format_type
        else:
            # Use default format or extension-based detection
            format_type = self._detect_format_by_extension(file_path)
        
        # Find appropriate parser
        parser = self._get_parser_for_format(format_type)
        
        if not parser or not parser.can_parse(file_path):
            raise NFOFormatError(
                f"No suitable parser found for file format: {format_type.value}",
                file_path=str(file_path),
                detected_format=format_type.value,
                supported_formats=list(self.parsers.keys())
            )
        
        # Parse the file
        nfo_data = parser.parse(file_path)
        
        # Cache the result
        self._file_cache[file_key] = nfo_data
        
        return nfo_data
    
    def edit_file(
        self,
        file_path: Union[str, Path],
        field_updates: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        output_format: Optional[str] = None
    ) -> EditResult:
        """
        Edit a single NFO file.
        
        Args:
            file_path: Path to the NFO file to edit
            field_updates: Dictionary of field names and new values
            output_path: Optional output path (defaults to original path)
            output_format: Optional output format (defaults to original or preserved format)
            
        Returns:
            EditResult object with operation details
        """
        import time
        start_time = time.time()
        
        file_path = Path(file_path)
        result = EditResult(file_path=file_path, success=False)
        
        try:
            # Load the file
            nfo_data = self.load_file(file_path)
            result.original_format = nfo_data.format_type
            
            # Apply field updates
            updated_fields = {}
            for field_name, new_value in field_updates.items():
                try:
                    old_value = nfo_data.get_field(field_name)
                    nfo_data.set_field(field_name, new_value)
                    updated_fields[field_name] = {'old': old_value, 'new': new_value}
                except NFOFieldError as e:
                    result.warnings.append(f"Failed to update field '{field_name}': {str(e)}")
            
            result.fields_updated = updated_fields
            
            # Determine output format
            if output_format:
                result.output_format = output_format
            elif self.preserve_format:
                result.output_format = nfo_data.format_type
            else:
                result.output_format = self.default_output_format
            
            # Save the file
            writer = self._get_writer_for_format(result.output_format)
            if not writer:
                raise NFOFormatError(
                    f"No writer available for format: {result.output_format}",
                    detected_format=result.output_format,
                    supported_formats=list(self.writers.keys())
                )
            
            output_file_path = writer.write(
                nfo_data,
                output_path=output_path,
                create_backup=self.create_backups
            )
            
            result.success = True
            result.file_path = output_file_path
            
            # Update cache
            self._file_cache[str(output_file_path)] = nfo_data
            
        except Exception as e:
            result.errors.append(str(e))
            self.logger.error(f"Failed to edit file {file_path}: {str(e)}")
        
        return result
    
    def batch_edit(
        self,
        field_updates: Dict[str, Any],
        file_pattern: Optional[str] = None,
        output_format: Optional[str] = None,
        max_files: Optional[int] = None
    ) -> BatchEditResult:
        """
        Edit multiple NFO files with the same field updates.
        
        Args:
            field_updates: Dictionary of field names and new values
            file_pattern: Optional pattern to filter files
            output_format: Optional output format for all files
            max_files: Optional maximum number of files to process
            
        Returns:
            BatchEditResult object with batch operation details
        """
        import time
        start_time = time.time()
        
        # Scan for files
        try:
            scan_result = self.scan_files(pattern=file_pattern)
            files_to_process = scan_result.nfo_files
        except Exception as e:
            return BatchEditResult(
                total_files=0,
                successful_edits=0,
                failed_edits=0,
                errors=[f"Failed to scan files: {str(e)}"],
                execution_time_seconds=time.time() - start_time
            )
        
        # Limit files if requested
        if max_files and len(files_to_process) > max_files:
            files_to_process = files_to_process[:max_files]
        
        # Process files
        results = []
        successful_count = 0
        failed_count = 0
        
        for file_path in files_to_process:
            try:
                result = self.edit_file(
                    file_path,
                    field_updates,
                    output_format=output_format
                )
                results.append(result)
                
                if result.success:
                    successful_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_result = EditResult(
                    file_path=file_path,
                    success=False,
                    errors=[str(e)]
                )
                results.append(failed_result)
                failed_count += 1
        
        return BatchEditResult(
            total_files=len(files_to_process),
            successful_edits=successful_count,
            failed_edits=failed_count,
            results=results,
            execution_time_seconds=time.time() - start_time
        )
    
    def preview_changes(
        self,
        field_updates: Dict[str, Any],
        file_pattern: Optional[str] = None,
        max_files: Optional[int] = 10
    ) -> Dict[str, Any]:
        """
        Preview what changes would be made without actually applying them.
        
        Args:
            field_updates: Dictionary of field names and new values
            file_pattern: Optional pattern to filter files
            max_files: Maximum number of files to preview
            
        Returns:
            Dictionary with preview information
        """
        # Scan for files
        scan_result = self.scan_files(pattern=file_pattern)
        files_to_preview = scan_result.nfo_files
        
        # Limit files
        if max_files and len(files_to_preview) > max_files:
            files_to_preview = files_to_preview[:max_files]
        
        preview_data = {
            'total_files_found': len(scan_result.nfo_files),
            'files_previewed': len(files_to_preview),
            'field_updates': field_updates,
            'file_previews': []
        }
        
        for file_path in files_to_preview:
            try:
                nfo_data = self.load_file(file_path)
                
                file_preview = {
                    'file_path': str(file_path),
                    'format': nfo_data.format_type,
                    'field_changes': {}
                }
                
                for field_name, new_value in field_updates.items():
                    current_value = nfo_data.get_field(field_name)
                    file_preview['field_changes'][field_name] = {
                        'current': current_value,
                        'new': new_value,
                        'will_change': current_value != new_value
                    }
                
                preview_data['file_previews'].append(file_preview)
                
            except Exception as e:
                preview_data['file_previews'].append({
                    'file_path': str(file_path),
                    'error': str(e)
                })
        
        return preview_data
    
    def _detect_format_by_extension(self, file_path: Path) -> NFOFormat:
        """
        Detect format based on file extension.
        
        Args:
            file_path: Path to analyze
            
        Returns:
            NFOFormat enum value
        """
        extension = file_path.suffix.lower()
        
        if extension in ['.xml']:
            return NFOFormat.XML
        elif extension in ['.json']:
            return NFOFormat.JSON
        else:
            return NFOFormat.TEXT
    
    def _get_parser_for_format(self, format_type: NFOFormat) -> Optional[BaseNFOParser]:
        """
        Get appropriate parser for format type.
        
        Args:
            format_type: Format type enum
            
        Returns:
            Parser instance or None
        """
        format_map = {
            NFOFormat.XML: 'xml',
            NFOFormat.JSON: 'json', 
            NFOFormat.TEXT: 'text'
        }
        
        parser_key = format_map.get(format_type)
        return self.parsers.get(parser_key) if parser_key else None
    
    def _get_writer_for_format(self, format_type: str) -> Optional[BaseNFOWriter]:
        """
        Get appropriate writer for format type.
        
        Args:
            format_type: Format type string
            
        Returns:
            Writer instance or None
        """
        return self.writers.get(format_type.lower())
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about an NFO file without fully loading it.
        
        Args:
            file_path: Path to the NFO file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        info = {
            'file_path': str(file_path),
            'exists': file_path.exists(),
            'size_bytes': 0,
            'format': 'unknown',
            'can_parse': False,
            'error': None
        }
        
        try:
            if file_path.exists():
                info['size_bytes'] = file_path.stat().st_size
                
                # Detect format
                if self.auto_detect_format:
                    detection_result = self.detector.detect_format(file_path)
                    info['format'] = detection_result.format_type.value
                    info['format_confidence'] = detection_result.confidence
                    info['format_details'] = detection_result.details
                
                # Check if we can parse it
                parser = self._get_parser_for_format(NFOFormat(info['format']))
                if parser:
                    info['can_parse'] = parser.can_parse(file_path)
        
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def clear_cache(self) -> None:
        """Clear the internal file cache."""
        self._file_cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current state of the editor.
        
        Returns:
            Dictionary with editor statistics
        """
        stats = {
            'directories_configured': len(self.directories),
            'cached_files': len(self._file_cache),
            'parsers_available': list(self.parsers.keys()),
            'writers_available': list(self.writers.keys()),
            'configuration': {
                'create_backups': self.create_backups,
                'auto_detect_format': self.auto_detect_format,
                'preserve_format': self.preserve_format,
                'default_output_format': self.default_output_format
            }
        }
        
        # Add directory scan statistics
        try:
            scan_result = self.scan_files()
            stats['scan_statistics'] = {
                'nfo_files_found': len(scan_result.nfo_files),
                'directories_scanned': scan_result.directories_scanned,
                'total_files_scanned': scan_result.total_files_scanned,
                'scan_errors': len(scan_result.errors)
            }
        except Exception as e:
            stats['scan_error'] = str(e)
        
        return stats
