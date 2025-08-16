"""
JSON writer for NFO files.

This module provides functionality to write NFO data back to JSON format files.
It supports various JSON structures and formatting options while maintaining
data integrity and readability.

Author: NFO Editor Team
"""

import json
from typing import Union, Optional, Dict, Any, List
from pathlib import Path

from .base import BaseNFOWriter
from ..parsers.base import NFOData
from ..utils.exceptions import NFOFormatError, NFOAccessError


class JSONNFOWriter(BaseNFOWriter):
    """
    Writer for JSON-formatted NFO files.
    
    This writer generates clean, well-formatted JSON files from NFOData objects.
    It supports various formatting options and can preserve original structure
    when possible.
    
    Attributes:
        format_name (str): Human-readable name of the format
        default_extension (str): Default file extension
        preserve_formatting (bool): Whether to preserve original formatting
        indent (Optional[int]): Number of spaces for indentation (None for compact)
        sort_keys (bool): Whether to sort keys alphabetically
        ensure_ascii (bool): Whether to escape non-ASCII characters
    """
    
    format_name = "JSON"
    default_extension = ".json"
    
    def __init__(
        self,
        preserve_formatting: bool = True,
        indent: Optional[int] = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        separators: Optional[tuple] = None
    ) -> None:
        """
        Initialize JSON writer.
        
        Args:
            preserve_formatting: Whether to preserve original formatting
            indent: Number of spaces for indentation (None for compact JSON)
            sort_keys: Whether to sort dictionary keys alphabetically
            ensure_ascii: Whether to escape non-ASCII characters
            separators: Optional tuple of (item_separator, dict_separator)
        """
        self.preserve_formatting = preserve_formatting
        self.indent = indent
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        self.separators = separators
    
    def can_write(self, nfo_data: NFOData) -> bool:
        """
        Check if this writer can handle the given NFO data format.
        
        Args:
            nfo_data: NFOData object to check
            
        Returns:
            True if this writer can handle the data format
        """
        # JSON writer can handle any NFOData object
        return True
    
    def write(
        self, 
        nfo_data: NFOData, 
        output_path: Optional[Union[str, Path]] = None,
        create_backup: bool = True
    ) -> Path:
        """
        Write NFO data to a JSON file.
        
        Args:
            nfo_data: NFOData object to write
            output_path: Optional output file path
            create_backup: Whether to create a backup of existing file
            
        Returns:
            Path to the written file
            
        Raises:
            NFOAccessError: If file cannot be written
            NFOFormatError: If data format is not supported
        """
        # Validate input data
        self._validate_nfo_data(nfo_data)
        
        # Determine output path
        output_path = self._get_output_path(nfo_data, output_path)
        
        # Create backup if requested and file exists
        backup_path = None
        if create_backup:
            backup_path = self._create_backup(output_path)
        
        try:
            # Generate JSON content
            json_content = self._generate_json_content(nfo_data)
            
            # Write to file
            self._write_file_content(json_content, output_path, nfo_data.encoding)
            
            # Preserve file metadata if original file existed
            if backup_path:
                self._preserve_file_metadata(backup_path, output_path)
            
            return Path(output_path)
            
        except Exception as e:
            raise NFOAccessError(
                f"Failed to write JSON file: {str(e)}",
                file_path=str(output_path),
                access_mode="write",
                system_error=str(e)
            ) from e
    
    def _generate_json_content(self, nfo_data: NFOData) -> str:
        """
        Generate JSON content from NFO data.
        
        Args:
            nfo_data: NFOData object to convert
            
        Returns:
            JSON content as string
        """
        # Prepare data for JSON serialization
        data_to_write = self._prepare_data_for_json(nfo_data.data)
        
        # Add metadata if it contains useful information
        if nfo_data.metadata and self._should_include_metadata(nfo_data.metadata):
            data_to_write = {
                'data': data_to_write,
                'metadata': self._filter_metadata(nfo_data.metadata)
            }
        
        try:
            # Generate JSON string
            json_str = json.dumps(
                data_to_write,
                indent=self.indent,
                sort_keys=self.sort_keys,
                ensure_ascii=self.ensure_ascii,
                separators=self.separators,
                default=self._json_serializer
            )
            
            return json_str
            
        except (TypeError, ValueError) as e:
            raise NFOFormatError(
                f"Failed to serialize data to JSON: {str(e)}",
                file_path=str(nfo_data.file_path),
                detected_format="JSON"
            ) from e
    
    def _prepare_data_for_json(self, data: Any) -> Any:
        """
        Prepare data for JSON serialization by handling non-serializable types.
        
        Args:
            data: Data to prepare
            
        Returns:
            JSON-serializable data
        """
        if isinstance(data, dict):
            return {key: self._prepare_data_for_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._prepare_data_for_json(item) for item in data]
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        else:
            # Convert other types to string
            return str(data)
    
    def _json_serializer(self, obj: Any) -> Any:
        """
        Custom JSON serializer for non-standard types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-serializable representation
        """
        # Handle Path objects
        if isinstance(obj, Path):
            return str(obj)
        
        # Handle other non-serializable types
        return str(obj)
    
    def _should_include_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Determine if metadata should be included in JSON output.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            True if metadata should be included
        """
        # Include metadata if it contains user-relevant information
        relevant_keys = {
            'original_structure', 'detected_structure', 'format_type',
            'creation_date', 'last_modified', 'source_file'
        }
        
        return any(key in metadata for key in relevant_keys)
    
    def _filter_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter metadata to include only relevant information for JSON output.
        
        Args:
            metadata: Original metadata
            
        Returns:
            Filtered metadata
        """
        filtered = {}
        
        # Include only user-relevant metadata
        include_keys = {
            'original_structure', 'detected_structure', 'format_type',
            'total_keys', 'max_depth', 'creation_date', 'last_modified'
        }
        
        for key, value in metadata.items():
            if key in include_keys:
                filtered[key] = self._prepare_data_for_json(value)
        
        return filtered
    
    def update_json_fields(
        self,
        nfo_data: NFOData,
        field_updates: Dict[str, Any],
        preserve_structure: bool = True
    ) -> str:
        """
        Update specific fields in JSON data while preserving structure.
        
        Args:
            nfo_data: Original NFO data
            field_updates: Dictionary of fields to update
            preserve_structure: Whether to preserve original JSON structure
            
        Returns:
            Updated JSON content as string
        """
        # Create updated data
        updated_data = self._deep_update_dict(nfo_data.data.copy(), field_updates)
        
        # Create new NFOData object with updates
        updated_nfo = NFOData(
            file_path=nfo_data.file_path,
            format_type=nfo_data.format_type,
            data=updated_data,
            metadata=nfo_data.metadata,
            encoding=nfo_data.encoding,
            is_modified=True
        )
        
        return self._generate_json_content(updated_nfo)
    
    def _deep_update_dict(self, base_dict: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deeply update a dictionary with new values.
        
        Args:
            base_dict: Base dictionary to update
            updates: Updates to apply
            
        Returns:
            Updated dictionary
        """
        for key, value in updates.items():
            if '.' in key:
                # Handle nested field updates (e.g., "movie.title")
                self._set_nested_field(base_dict, key, value)
            else:
                base_dict[key] = value
        
        return base_dict
    
    def _set_nested_field(self, data: Dict[str, Any], field_path: str, value: Any) -> None:
        """
        Set a nested field value using dot notation.
        
        Args:
            data: Dictionary to update
            field_path: Dot-separated field path
            value: Value to set
        """
        keys = field_path.split('.')
        current = data
        
        # Navigate to the parent of the target field
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def validate_json_output(self, json_content: str) -> Dict[str, Any]:
        """
        Validate generated JSON content.
        
        Args:
            json_content: JSON content to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'size_bytes': len(json_content.encode('utf-8')),
            'line_count': json_content.count('\n') + 1,
            'structure_info': {}
        }
        
        try:
            # Try to parse JSON
            parsed_data = json.loads(json_content)
            validation_result['is_valid'] = True
            
            # Analyze structure
            validation_result['structure_info'] = {
                'type': type(parsed_data).__name__,
                'total_keys': self._count_json_keys(parsed_data),
                'max_depth': self._calculate_json_depth(parsed_data),
                'has_arrays': self._contains_json_arrays(parsed_data),
                'empty_values': self._count_json_empty_values(parsed_data)
            }
            
            # Check for potential issues
            if validation_result['size_bytes'] > 1024 * 1024:  # 1MB
                validation_result['warnings'].append("Large file size (>1MB)")
            
            if validation_result['structure_info']['max_depth'] > 10:
                validation_result['warnings'].append("Deep nesting detected")
            
            if validation_result['structure_info']['empty_values'] > 0:
                validation_result['warnings'].append("Contains empty values")
            
        except json.JSONDecodeError as e:
            validation_result['errors'].append(f"JSON parsing error: {str(e)}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _count_json_keys(self, data: Any) -> int:
        """Count total keys in JSON structure."""
        if isinstance(data, dict):
            count = len(data)
            for value in data.values():
                count += self._count_json_keys(value)
            return count
        elif isinstance(data, list):
            return sum(self._count_json_keys(item) for item in data)
        return 0
    
    def _calculate_json_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of JSON structure."""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(
                self._calculate_json_depth(value, current_depth + 1)
                for value in data.values()
            )
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(
                self._calculate_json_depth(item, current_depth + 1)
                for item in data
            )
        return current_depth
    
    def _contains_json_arrays(self, data: Any) -> bool:
        """Check if JSON structure contains arrays."""
        if isinstance(data, list):
            return True
        elif isinstance(data, dict):
            return any(self._contains_json_arrays(value) for value in data.values())
        return False
    
    def _count_json_empty_values(self, data: Any) -> int:
        """Count empty values in JSON structure."""
        count = 0
        if isinstance(data, dict):
            for value in data.values():
                if value is None or value == "" or value == [] or value == {}:
                    count += 1
                else:
                    count += self._count_json_empty_values(value)
        elif isinstance(data, list):
            for item in data:
                if item is None or item == "" or item == [] or item == {}:
                    count += 1
                else:
                    count += self._count_json_empty_values(item)
        return count
    
    def create_compact_json(self, nfo_data: NFOData) -> str:
        """
        Create compact JSON without indentation.
        
        Args:
            nfo_data: NFOData object to convert
            
        Returns:
            Compact JSON string
        """
        # Temporarily override formatting settings
        original_indent = self.indent
        original_separators = self.separators
        
        self.indent = None
        self.separators = (',', ':')
        
        try:
            return self._generate_json_content(nfo_data)
        finally:
            # Restore original settings
            self.indent = original_indent
            self.separators = original_separators
    
    def create_pretty_json(self, nfo_data: NFOData, indent: int = 4) -> str:
        """
        Create pretty-formatted JSON with custom indentation.
        
        Args:
            nfo_data: NFOData object to convert
            indent: Number of spaces for indentation
            
        Returns:
            Pretty-formatted JSON string
        """
        # Temporarily override indent setting
        original_indent = self.indent
        self.indent = indent
        
        try:
            return self._generate_json_content(nfo_data)
        finally:
            # Restore original setting
            self.indent = original_indent
