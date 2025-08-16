"""
Base classes and interfaces for NFO file parsers.

This module defines the abstract base class that all NFO parsers must implement,
along with the NFOData class that represents parsed NFO file content.

Author: NFO Editor Team
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field

from ..utils.exceptions import NFOParseError, NFOFieldError


@dataclass
class NFOData:
    """
    Data structure representing parsed NFO file content.
    
    This class provides a unified interface for accessing and modifying
    NFO file data regardless of the original format (XML, JSON, text, etc.).
    
    Attributes:
        file_path (Path): Path to the original NFO file
        format_type (str): Detected format type (xml, json, text)
        data (Dict[str, Any]): Dictionary containing the parsed NFO data
        metadata (Dict[str, Any]): Additional metadata about the file/parsing
        is_modified (bool): Whether the data has been modified since parsing
        encoding (str): Character encoding of the original file
    """
    
    file_path: Path
    format_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_modified: bool = False
    encoding: str = "utf-8"
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """
        Get the value of a specific field.
        
        Args:
            field_name: Name of the field to retrieve
            default: Default value if field is not found
            
        Returns:
            Field value or default if not found
            
        Raises:
            NFOFieldError: If field access fails for reasons other than not found
        """
        try:
            # Support nested field access with dot notation (e.g., "movie.title")
            keys = field_name.split('.')
            current = self.data
            
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                    if current is None:
                        return default
                else:
                    return default
                    
            return current if current is not None else default
            
        except Exception as e:
            raise NFOFieldError(
                f"Failed to get field '{field_name}': {str(e)}",
                field_name=field_name,
                operation="get",
                file_path=str(self.file_path)
            ) from e
    
    def set_field(self, field_name: str, value: Any) -> None:
        """
        Set the value of a specific field.
        
        Args:
            field_name: Name of the field to set
            value: Value to set
            
        Raises:
            NFOFieldError: If field setting fails
        """
        try:
            # Support nested field creation with dot notation
            keys = field_name.split('.')
            current = self.data
            
            # Navigate/create nested structure
            for key in keys[:-1]:
                if not isinstance(current, dict):
                    raise NFOFieldError(
                        f"Cannot set nested field '{field_name}': parent is not a dictionary",
                        field_name=field_name,
                        operation="set",
                        file_path=str(self.file_path)
                    )
                
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the final value
            if not isinstance(current, dict):
                raise NFOFieldError(
                    f"Cannot set field '{keys[-1]}': parent is not a dictionary",
                    field_name=field_name,
                    operation="set", 
                    file_path=str(self.file_path)
                )
                
            current[keys[-1]] = value
            self.is_modified = True
            
        except NFOFieldError:
            raise
        except Exception as e:
            raise NFOFieldError(
                f"Failed to set field '{field_name}': {str(e)}",
                field_name=field_name,
                field_value=value,
                operation="set",
                file_path=str(self.file_path)
            ) from e
    
    def has_field(self, field_name: str) -> bool:
        """
        Check if a field exists.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field exists, False otherwise
        """
        try:
            value = self.get_field(field_name)
            return value is not None
        except NFOFieldError:
            return False
    
    def delete_field(self, field_name: str) -> bool:
        """
        Delete a field.
        
        Args:
            field_name: Name of the field to delete
            
        Returns:
            True if field was deleted, False if it didn't exist
            
        Raises:
            NFOFieldError: If deletion fails
        """
        try:
            keys = field_name.split('.')
            current = self.data
            
            # Navigate to parent
            for key in keys[:-1]:
                if not isinstance(current, dict) or key not in current:
                    return False  # Field doesn't exist
                current = current[key]
            
            # Delete the field
            if isinstance(current, dict) and keys[-1] in current:
                del current[keys[-1]]
                self.is_modified = True
                return True
            
            return False
            
        except Exception as e:
            raise NFOFieldError(
                f"Failed to delete field '{field_name}': {str(e)}",
                field_name=field_name,
                operation="delete",
                file_path=str(self.file_path)
            ) from e
    
    def get_all_fields(self) -> Dict[str, Any]:
        """
        Get all fields as a flat dictionary with dot notation keys.
        
        Returns:
            Dictionary with all fields using dot notation for nested keys
        """
        def _flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
            """Recursively flatten nested dictionaries."""
            result = {}
            for key, value in d.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    result.update(_flatten_dict(value, new_key))
                else:
                    result[new_key] = value
            return result
        
        return _flatten_dict(self.data)
    
    def update_fields(self, field_updates: Dict[str, Any]) -> None:
        """
        Update multiple fields at once.
        
        Args:
            field_updates: Dictionary of field names and values to update
            
        Raises:
            NFOFieldError: If any field update fails
        """
        for field_name, value in field_updates.items():
            self.set_field(field_name, value)


class BaseNFOParser(ABC):
    """
    Abstract base class for all NFO file parsers.
    
    This class defines the interface that all NFO parsers must implement.
    Concrete parser classes should inherit from this class and implement
    the abstract methods for their specific file format.
    
    Attributes:
        supported_extensions (List[str]): File extensions this parser supports
        format_name (str): Human-readable name of the format
    """
    
    supported_extensions: List[str] = []
    format_name: str = "Unknown"
    
    @abstractmethod
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this parser can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> NFOData:
        """
        Parse an NFO file and return structured data.
        
        Args:
            file_path: Path to the NFO file to parse
            
        Returns:
            NFOData object containing the parsed information
            
        Raises:
            NFOParseError: If parsing fails
            NFOAccessError: If file cannot be read
        """
        pass
    
    def _detect_encoding(self, file_path: Union[str, Path]) -> str:
        """
        Detect the character encoding of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        import chardet
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') or 'utf-8'
            
        except Exception:
            # Fall back to utf-8 if detection fails
            return 'utf-8'
    
    def _read_file_content(self, file_path: Union[str, Path], encoding: str = None) -> str:
        """
        Read file content with proper encoding handling.
        
        Args:
            file_path: Path to the file
            encoding: Character encoding to use (auto-detected if None)
            
        Returns:
            File content as string
            
        Raises:
            NFOAccessError: If file cannot be read
        """
        from ..utils.exceptions import NFOAccessError
        
        try:
            if encoding is None:
                encoding = self._detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
                
        except IOError as e:
            raise NFOAccessError(
                f"Cannot read file: {str(e)}",
                file_path=str(file_path),
                access_mode="read",
                system_error=str(e)
            ) from e
        except UnicodeDecodeError as e:
            raise NFOAccessError(
                f"Cannot decode file with encoding {encoding}: {str(e)}",
                file_path=str(file_path),
                access_mode="read",
                system_error=str(e)
            ) from e
