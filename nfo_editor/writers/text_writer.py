"""
Plain text writer for NFO files.

This module provides functionality to write NFO data back to plain text format
files with various formatting options including key-value pairs, sections,
and structured layouts.

Author: NFO Editor Team
"""

from typing import Union, Optional, Dict, Any, List
from pathlib import Path
import textwrap

from .base import BaseNFOWriter
from ..parsers.base import NFOData
from ..utils.exceptions import NFOFormatError, NFOAccessError


class TextNFOWriter(BaseNFOWriter):
    """
    Writer for plain text NFO files.
    
    This writer can generate various text formats including key-value pairs,
    sectioned content, and free-form text layouts. It provides flexible
    formatting options while maintaining readability.
    
    Attributes:
        format_name (str): Human-readable name of the format
        default_extension (str): Default file extension
        preserve_formatting (bool): Whether to preserve original formatting
        delimiter (str): Delimiter for key-value pairs
        section_header_style (str): Style for section headers
        line_width (int): Maximum line width for text wrapping
        indent_size (int): Number of spaces for indentation
    """
    
    format_name = "Text"
    default_extension = ".nfo"
    
    def __init__(
        self,
        preserve_formatting: bool = True,
        delimiter: str = ": ",
        section_header_style: str = "brackets",  # brackets, equals, dashes
        line_width: int = 80,
        indent_size: int = 2,
        sort_fields: bool = False
    ) -> None:
        """
        Initialize text writer.
        
        Args:
            preserve_formatting: Whether to preserve original formatting
            delimiter: Delimiter for key-value pairs (e.g., ": ", " = ", " | ")
            section_header_style: Style for section headers
            line_width: Maximum line width for text wrapping (0 for no wrapping)
            indent_size: Number of spaces for indentation
            sort_fields: Whether to sort fields alphabetically
        """
        self.preserve_formatting = preserve_formatting
        self.delimiter = delimiter
        self.section_header_style = section_header_style
        self.line_width = line_width
        self.indent_size = indent_size
        self.sort_fields = sort_fields
    
    def can_write(self, nfo_data: NFOData) -> bool:
        """
        Check if this writer can handle the given NFO data format.
        
        Args:
            nfo_data: NFOData object to check
            
        Returns:
            True if this writer can handle the data format
        """
        # Text writer can handle any NFOData object
        return True
    
    def write(
        self, 
        nfo_data: NFOData, 
        output_path: Optional[Union[str, Path]] = None,
        create_backup: bool = True
    ) -> Path:
        """
        Write NFO data to a text file.
        
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
            # Generate text content
            text_content = self._generate_text_content(nfo_data)
            
            # Write to file
            self._write_file_content(text_content, output_path, nfo_data.encoding)
            
            # Preserve file metadata if original file existed
            if backup_path:
                self._preserve_file_metadata(backup_path, output_path)
            
            return Path(output_path)
            
        except Exception as e:
            raise NFOAccessError(
                f"Failed to write text file: {str(e)}",
                file_path=str(output_path),
                access_mode="write",
                system_error=str(e)
            ) from e
    
    def _generate_text_content(self, nfo_data: NFOData) -> str:
        """
        Generate text content from NFO data.
        
        Args:
            nfo_data: NFOData object to convert
            
        Returns:
            Text content as string
        """
        # Determine if data has sections
        has_sections = self._detect_sections(nfo_data.data)
        
        if has_sections:
            return self._generate_sectioned_text(nfo_data)
        else:
            return self._generate_key_value_text(nfo_data)
    
    def _detect_sections(self, data: Dict[str, Any]) -> bool:
        """
        Detect if data should be organized into sections.
        
        Args:
            data: Data dictionary to analyze
            
        Returns:
            True if data should be sectioned
        """
        # Consider data sectioned if it has nested dictionaries
        # or if metadata indicates original structure was sectioned
        for value in data.values():
            if isinstance(value, dict):
                return True
        
        return False
    
    def _generate_sectioned_text(self, nfo_data: NFOData) -> str:
        """
        Generate text content with sections.
        
        Args:
            nfo_data: NFOData object to convert
            
        Returns:
            Sectioned text content
        """
        lines = []
        data = nfo_data.data
        
        # Add file header if metadata available
        if nfo_data.metadata:
            header = self._generate_header(nfo_data.metadata)
            if header:
                lines.extend(header)
                lines.append("")  # Empty line after header
        
        # Process sections
        sections = data.items()
        if self.sort_fields:
            sections = sorted(sections)
        
        for section_name, section_data in sections:
            if isinstance(section_data, dict):
                # Section with structured data
                lines.append(self._format_section_header(section_name))
                lines.extend(self._format_section_content(section_data))
                lines.append("")  # Empty line after section
            else:
                # Simple key-value pair
                formatted_line = self._format_field(section_name, section_data)
                lines.extend(formatted_line)
        
        # Remove trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()
        
        return "\n".join(lines)
    
    def _generate_key_value_text(self, nfo_data: NFOData) -> str:
        """
        Generate simple key-value text content.
        
        Args:
            nfo_data: NFOData object to convert
            
        Returns:
            Key-value text content
        """
        lines = []
        data = nfo_data.data
        
        # Add file header if metadata available
        if nfo_data.metadata:
            header = self._generate_header(nfo_data.metadata)
            if header:
                lines.extend(header)
                lines.append("")  # Empty line after header
        
        # Process fields
        fields = data.items()
        if self.sort_fields:
            fields = sorted(fields)
        
        for key, value in fields:
            formatted_lines = self._format_field(key, value)
            lines.extend(formatted_lines)
        
        # Remove trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()
        
        return "\n".join(lines)
    
    def _format_section_header(self, section_name: str) -> str:
        """
        Format a section header according to the configured style.
        
        Args:
            section_name: Name of the section
            
        Returns:
            Formatted section header
        """
        clean_name = self._format_field_name(section_name)
        
        if self.section_header_style == "brackets":
            return f"[{clean_name}]"
        elif self.section_header_style == "equals":
            return f"=== {clean_name} ==="
        elif self.section_header_style == "dashes":
            return f"--- {clean_name} ---"
        else:
            # Default to brackets
            return f"[{clean_name}]"
    
    def _format_section_content(self, section_data: Dict[str, Any]) -> List[str]:
        """
        Format the content of a section.
        
        Args:
            section_data: Section data dictionary
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        fields = section_data.items()
        if self.sort_fields:
            fields = sorted(fields)
        
        for key, value in fields:
            formatted_lines = self._format_field(key, value, indent=True)
            lines.extend(formatted_lines)
        
        return lines
    
    def _format_field(self, key: str, value: Any, indent: bool = False) -> List[str]:
        """
        Format a single field (key-value pair).
        
        Args:
            key: Field name
            value: Field value
            indent: Whether to indent the field
            
        Returns:
            List of formatted lines for this field
        """
        lines = []
        formatted_key = self._format_field_name(key)
        indent_str = " " * self.indent_size if indent else ""
        
        if isinstance(value, list):
            # Handle list values
            if len(value) == 1:
                # Single item list - format as simple value
                formatted_value = self._format_field_value(value[0])
                line = f"{indent_str}{formatted_key}{self.delimiter}{formatted_value}"
                lines.extend(self._wrap_line(line))
            else:
                # Multiple items - format as multi-line
                lines.append(f"{indent_str}{formatted_key}:")
                for item in value:
                    formatted_item = self._format_field_value(item)
                    item_line = f"{indent_str}  - {formatted_item}"
                    lines.extend(self._wrap_line(item_line))
        
        elif isinstance(value, dict):
            # Handle nested dictionary
            lines.append(f"{indent_str}{formatted_key}:")
            for sub_key, sub_value in value.items():
                sub_lines = self._format_field(sub_key, sub_value, indent=True)
                lines.extend([f"  {line}" for line in sub_lines])
        
        else:
            # Handle simple values
            formatted_value = self._format_field_value(value)
            line = f"{indent_str}{formatted_key}{self.delimiter}{formatted_value}"
            lines.extend(self._wrap_line(line))
        
        return lines
    
    def _format_field_name(self, name: str) -> str:
        """
        Format a field name for display.
        
        Args:
            name: Raw field name
            
        Returns:
            Formatted field name
        """
        if not name:
            return "Unknown"
        
        # Convert underscores to spaces and capitalize
        formatted = name.replace('_', ' ')
        
        # Capitalize words
        formatted = ' '.join(word.capitalize() for word in formatted.split())
        
        return formatted
    
    def _format_field_value(self, value: Any) -> str:
        """
        Format a field value for display.
        
        Args:
            value: Field value
            
        Returns:
            Formatted field value string
        """
        if value is None:
            return ""
        elif isinstance(value, bool):
            return "Yes" if value else "No"
        elif isinstance(value, (list, dict)):
            # These should be handled separately, but just in case
            return str(value)
        else:
            return str(value)
    
    def _wrap_line(self, line: str) -> List[str]:
        """
        Wrap a line to the configured line width.
        
        Args:
            line: Line to wrap
            
        Returns:
            List of wrapped lines
        """
        if self.line_width <= 0 or len(line) <= self.line_width:
            return [line]
        
        # Find the delimiter position to preserve key-value alignment
        if self.delimiter in line:
            key_part, value_part = line.split(self.delimiter, 1)
            key_length = len(key_part) + len(self.delimiter)
            
            # Wrap the value part with proper indentation
            wrapped_value = textwrap.fill(
                value_part,
                width=self.line_width,
                initial_indent="",
                subsequent_indent=" " * key_length
            )
            
            return [key_part + self.delimiter + wrapped_value]
        else:
            # No delimiter found, wrap normally
            return textwrap.wrap(line, width=self.line_width)
    
    def _generate_header(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Generate file header with metadata information.
        
        Args:
            metadata: NFO metadata
            
        Returns:
            List of header lines
        """
        header_lines = []
        
        # Add relevant metadata as comments
        relevant_metadata = {
            'format_type': 'Format',
            'detected_structure': 'Structure', 
            'field_count': 'Fields',
            'line_count': 'Lines'
        }
        
        for meta_key, display_name in relevant_metadata.items():
            if meta_key in metadata and metadata[meta_key]:
                header_lines.append(f"# {display_name}: {metadata[meta_key]}")
        
        return header_lines
    
    def update_text_fields(
        self,
        nfo_data: NFOData,
        field_updates: Dict[str, Any]
    ) -> str:
        """
        Update specific fields in text data.
        
        Args:
            nfo_data: Original NFO data
            field_updates: Dictionary of fields to update
            
        Returns:
            Updated text content as string
        """
        # Update data
        updated_data = nfo_data.data.copy()
        for field_path, new_value in field_updates.items():
            self._set_nested_field(updated_data, field_path, new_value)
        
        # Create updated NFOData object
        updated_nfo = NFOData(
            file_path=nfo_data.file_path,
            format_type=nfo_data.format_type,
            data=updated_data,
            metadata=nfo_data.metadata,
            encoding=nfo_data.encoding,
            is_modified=True
        )
        
        return self._generate_text_content(updated_nfo)
    
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
            elif not isinstance(current[key], dict):
                # Convert non-dict values to dict
                current[key] = {'value': current[key]}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def create_summary_text(self, nfo_data: NFOData, max_fields: int = 10) -> str:
        """
        Create a summary text version with only the most important fields.
        
        Args:
            nfo_data: NFOData object to summarize
            max_fields: Maximum number of fields to include
            
        Returns:
            Summary text content
        """
        # Priority fields for summary
        priority_fields = [
            'title', 'name', 'plot', 'summary', 'description',
            'year', 'genre', 'rating', 'runtime', 'director',
            'artist', 'album', 'track'
        ]
        
        summary_data = {}
        
        # Extract priority fields
        flat_data = self._flatten_data(nfo_data.data)
        
        for priority_field in priority_fields:
            for key, value in flat_data.items():
                if priority_field.lower() in key.lower():
                    summary_data[key] = value
                    break
            
            if len(summary_data) >= max_fields:
                break
        
        # Fill remaining slots with any other fields
        for key, value in flat_data.items():
            if key not in summary_data:
                summary_data[key] = value
                if len(summary_data) >= max_fields:
                    break
        
        # Create summary NFOData object
        summary_nfo = NFOData(
            file_path=nfo_data.file_path,
            format_type=nfo_data.format_type,
            data=summary_data,
            metadata={'summary': True},
            encoding=nfo_data.encoding
        )
        
        return self._generate_text_content(summary_nfo)
    
    def _flatten_data(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """
        Flatten nested dictionary structure.
        
        Args:
            data: Dictionary to flatten
            prefix: Prefix for keys
            
        Returns:
            Flattened dictionary
        """
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_data(value, new_key))
            else:
                flattened[new_key] = value
        
        return flattened
