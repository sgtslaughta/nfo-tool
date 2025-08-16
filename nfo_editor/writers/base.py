"""
Base classes and interfaces for NFO file writers.

This module defines the abstract base class that all NFO writers must implement.
Writers are responsible for serializing NFOData objects back to files in their
respective formats.

Author: NFO Editor Team
"""

from abc import ABC, abstractmethod
from typing import Union, Optional
from pathlib import Path

from ..parsers.base import NFOData
from ..utils.exceptions import NFOAccessError, NFOFormatError


class BaseNFOWriter(ABC):
    """
    Abstract base class for all NFO file writers.
    
    This class defines the interface that all NFO writers must implement.
    Concrete writer classes should inherit from this class and implement
    the abstract methods for their specific file format.
    
    Attributes:
        format_name (str): Human-readable name of the format this writer handles
        default_extension (str): Default file extension for this format
        preserve_formatting (bool): Whether to preserve original formatting when possible
    """
    
    format_name: str = "Unknown"
    default_extension: str = ".nfo"
    preserve_formatting: bool = True
    
    @abstractmethod
    def can_write(self, nfo_data: NFOData) -> bool:
        """
        Check if this writer can handle the given NFO data format.
        
        Args:
            nfo_data: NFOData object to check
            
        Returns:
            True if this writer can handle the data format, False otherwise
        """
        pass
    
    @abstractmethod
    def write(
        self, 
        nfo_data: NFOData, 
        output_path: Optional[Union[str, Path]] = None,
        create_backup: bool = True
    ) -> Path:
        """
        Write NFO data to a file.
        
        Args:
            nfo_data: NFOData object to write
            output_path: Optional output file path (uses original path if None)
            create_backup: Whether to create a backup of the existing file
            
        Returns:
            Path to the written file
            
        Raises:
            NFOAccessError: If file cannot be written
            NFOFormatError: If data format is not supported by this writer
        """
        pass
    
    def _create_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """
        Create a backup copy of an existing file.
        
        Args:
            file_path: Path to the file to back up
            
        Returns:
            Path to the backup file, or None if no backup was needed
            
        Raises:
            NFOAccessError: If backup creation fails
        """
        import shutil
        from datetime import datetime
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None  # No file to back up
            
        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}.{timestamp}.backup{file_path.suffix}"
            backup_path = file_path.parent / backup_name
            
            shutil.copy2(file_path, backup_path)
            return backup_path
            
        except Exception as e:
            raise NFOAccessError(
                f"Failed to create backup: {str(e)}",
                file_path=str(file_path),
                access_mode="backup",
                system_error=str(e)
            ) from e
    
    def _write_file_content(
        self, 
        content: str, 
        file_path: Union[str, Path], 
        encoding: str = "utf-8"
    ) -> None:
        """
        Write content to a file with proper error handling.
        
        Args:
            content: Content to write
            file_path: Path to write to
            encoding: Character encoding to use
            
        Raises:
            NFOAccessError: If file cannot be written
        """
        try:
            # Ensure parent directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
                
        except IOError as e:
            raise NFOAccessError(
                f"Cannot write file: {str(e)}",
                file_path=str(file_path),
                access_mode="write",
                system_error=str(e)
            ) from e
        except UnicodeEncodeError as e:
            raise NFOAccessError(
                f"Cannot encode content with encoding {encoding}: {str(e)}",
                file_path=str(file_path),
                access_mode="write",
                system_error=str(e)
            ) from e
    
    def _validate_nfo_data(self, nfo_data: NFOData) -> None:
        """
        Validate NFO data before writing.
        
        Args:
            nfo_data: NFOData object to validate
            
        Raises:
            NFOFormatError: If data is invalid for this format
        """
        if not isinstance(nfo_data, NFOData):
            raise NFOFormatError(
                "Invalid data type: expected NFOData object",
                detected_format=type(nfo_data).__name__,
                supported_formats=[NFOData.__name__]
            )
        
        if not self.can_write(nfo_data):
            raise NFOFormatError(
                f"This writer cannot handle '{nfo_data.format_type}' format",
                detected_format=nfo_data.format_type,
                supported_formats=[self.format_name]
            )
    
    def _get_output_path(
        self, 
        nfo_data: NFOData, 
        output_path: Optional[Union[str, Path]]
    ) -> Path:
        """
        Determine the output file path.
        
        Args:
            nfo_data: NFOData object
            output_path: Optional explicit output path
            
        Returns:
            Path object for the output file
        """
        if output_path is not None:
            return Path(output_path)
        
        # Use original file path
        original_path = nfo_data.file_path
        
        # Ensure the file has the correct extension for this format
        if not original_path.suffix.lower() == self.default_extension.lower():
            return original_path.with_suffix(self.default_extension)
        
        return original_path
    
    def _preserve_file_metadata(self, source_path: Path, target_path: Path) -> None:
        """
        Preserve file metadata (permissions, timestamps) from source to target.
        
        Args:
            source_path: Source file path
            target_path: Target file path
        """
        import os
        import shutil
        
        try:
            if source_path.exists() and target_path.exists():
                # Copy file metadata (timestamps, permissions)
                shutil.copystat(source_path, target_path)
        except Exception:
            # Silently fail if metadata preservation fails
            # This is not critical for the core functionality
            pass
