"""
XML writer for NFO files.

This module provides functionality to write NFO data back to XML format files.
It supports various XML structures and can preserve or recreate formatting
based on configuration options.

Author: NFO Editor Team
"""

import xml.etree.ElementTree as ET
from typing import Union, Optional, Dict, Any, List
from pathlib import Path
import xml.dom.minidom as minidom

from .base import BaseNFOWriter
from ..parsers.base import NFOData
from ..utils.exceptions import NFOFormatError, NFOAccessError


class XMLNFOWriter(BaseNFOWriter):
    """
    Writer for XML-formatted NFO files.
    
    This writer can generate XML NFO files with proper formatting and structure.
    It supports both simple and complex XML hierarchies and can preserve
    original formatting when possible.
    
    Attributes:
        format_name (str): Human-readable name of the format
        default_extension (str): Default file extension
        preserve_formatting (bool): Whether to preserve original formatting
        pretty_print (bool): Whether to format XML with proper indentation
        xml_declaration (bool): Whether to include XML declaration
        encoding (str): Character encoding for XML output
    """
    
    format_name = "XML"
    default_extension = ".xml"
    
    def __init__(
        self,
        preserve_formatting: bool = True,
        pretty_print: bool = True,
        xml_declaration: bool = True,
        encoding: str = "utf-8",
        root_element: str = "nfo"
    ) -> None:
        """
        Initialize XML writer.
        
        Args:
            preserve_formatting: Whether to preserve original formatting
            pretty_print: Whether to format XML with proper indentation
            xml_declaration: Whether to include XML declaration
            encoding: Character encoding for XML output
            root_element: Name of the root XML element
        """
        self.preserve_formatting = preserve_formatting
        self.pretty_print = pretty_print
        self.xml_declaration = xml_declaration
        self.encoding = encoding
        self.root_element = root_element
    
    def can_write(self, nfo_data: NFOData) -> bool:
        """
        Check if this writer can handle the given NFO data format.
        
        Args:
            nfo_data: NFOData object to check
            
        Returns:
            True if this writer can handle the data format
        """
        # XML writer can handle any NFOData object
        return True
    
    def write(
        self, 
        nfo_data: NFOData, 
        output_path: Optional[Union[str, Path]] = None,
        create_backup: bool = True
    ) -> Path:
        """
        Write NFO data to an XML file.
        
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
            # Generate XML content
            xml_content = self._generate_xml_content(nfo_data)
            
            # Write to file
            self._write_file_content(xml_content, output_path, nfo_data.encoding)
            
            # Preserve file metadata if original file existed
            if backup_path:
                self._preserve_file_metadata(backup_path, output_path)
            
            return Path(output_path)
            
        except Exception as e:
            # If backup was created and write failed, could restore here
            raise NFOAccessError(
                f"Failed to write XML file: {str(e)}",
                file_path=str(output_path),
                access_mode="write",
                system_error=str(e)
            ) from e
    
    def _generate_xml_content(self, nfo_data: NFOData) -> str:
        """
        Generate XML content from NFO data.
        
        Args:
            nfo_data: NFOData object to convert
            
        Returns:
            XML content as string
        """
        # Determine root element name
        root_name = self.root_element
        if nfo_data.metadata.get('root_element'):
            root_name = nfo_data.metadata['root_element']
        elif nfo_data.format_type == "xml" and 'root_element' in nfo_data.metadata:
            root_name = nfo_data.metadata['root_element']
        
        # Create XML structure
        root = ET.Element(root_name)
        
        # Add XML namespaces if they were preserved
        namespaces = nfo_data.metadata.get('xml_namespaces', {})
        for prefix, uri in namespaces.items():
            if prefix == 'default':
                root.set('xmlns', uri)
            else:
                root.set(f'xmlns:{prefix}', uri)
        
        # Convert data dictionary to XML elements
        self._dict_to_xml(nfo_data.data, root)
        
        # Generate XML string
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        
        # Add XML declaration if requested
        if self.xml_declaration:
            declaration = f'<?xml version="1.0" encoding="{self.encoding}"?>\n'
            xml_str = declaration + xml_str
        
        # Pretty print if requested
        if self.pretty_print:
            xml_str = self._pretty_print_xml(xml_str)
        
        return xml_str
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: ET.Element) -> None:
        """
        Convert dictionary data to XML elements.
        
        Args:
            data: Dictionary data to convert
            parent: Parent XML element to add children to
        """
        for key, value in data.items():
            if key.startswith('@'):
                # Handle attributes
                attr_name = key[1:]  # Remove @ prefix
                parent.set(attr_name, str(value))
            elif key == '#text':
                # Handle element text content
                parent.text = str(value)
            else:
                # Handle child elements
                self._create_child_element(key, value, parent)
    
    def _create_child_element(self, key: str, value: Any, parent: ET.Element) -> None:
        """
        Create child XML elements from key-value pairs.
        
        Args:
            key: Element name
            value: Element value or nested data
            parent: Parent XML element
        """
        if isinstance(value, dict):
            # Nested dictionary - create element with children
            child = ET.SubElement(parent, key)
            self._dict_to_xml(value, child)
            
        elif isinstance(value, list):
            # List of values - create multiple elements with same name
            for item in value:
                child = ET.SubElement(parent, key)
                if isinstance(item, dict):
                    self._dict_to_xml(item, child)
                else:
                    child.text = str(item)
                    
        else:
            # Simple value - create element with text content
            child = ET.SubElement(parent, key)
            child.text = str(value)
    
    def _pretty_print_xml(self, xml_str: str) -> str:
        """
        Pretty print XML with proper indentation.
        
        Args:
            xml_str: Raw XML string
            
        Returns:
            Pretty formatted XML string
        """
        try:
            # Parse and pretty print using minidom
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ", encoding=None)
            
            # Remove extra blank lines and the extra XML declaration
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            
            # Remove the minidom XML declaration if we're adding our own
            if self.xml_declaration and lines and lines[0].startswith('<?xml'):
                lines = lines[1:]
            
            return '\n'.join(lines)
            
        except Exception:
            # If pretty printing fails, return original
            return xml_str
    
    def update_existing_xml(
        self, 
        nfo_data: NFOData, 
        field_updates: Dict[str, Any],
        preserve_structure: bool = True
    ) -> str:
        """
        Update existing XML content with new field values.
        
        This method attempts to preserve the original XML structure
        while updating only the specified fields.
        
        Args:
            nfo_data: Original NFO data
            field_updates: Dictionary of fields to update
            preserve_structure: Whether to preserve original XML structure
            
        Returns:
            Updated XML content as string
        """
        if nfo_data.format_type != "xml" or not preserve_structure:
            # Fall back to regenerating entire XML
            updated_data = NFOData(
                file_path=nfo_data.file_path,
                format_type=nfo_data.format_type,
                data={**nfo_data.data, **field_updates},
                metadata=nfo_data.metadata,
                encoding=nfo_data.encoding
            )
            return self._generate_xml_content(updated_data)
        
        # Try to update existing XML structure
        try:
            # Read original XML file
            original_content = self._read_original_xml(nfo_data.file_path)
            root = ET.fromstring(original_content)
            
            # Update fields in XML tree
            for field_path, new_value in field_updates.items():
                self._update_xml_field(root, field_path, new_value)
            
            # Generate updated XML
            xml_str = ET.tostring(root, encoding='unicode', method='xml')
            
            if self.xml_declaration:
                declaration = f'<?xml version="1.0" encoding="{self.encoding}"?>\n'
                xml_str = declaration + xml_str
            
            if self.pretty_print:
                xml_str = self._pretty_print_xml(xml_str)
            
            return xml_str
            
        except Exception:
            # Fall back to regenerating entire XML
            updated_data = NFOData(
                file_path=nfo_data.file_path,
                format_type=nfo_data.format_type,
                data={**nfo_data.data, **field_updates},
                metadata=nfo_data.metadata,
                encoding=nfo_data.encoding
            )
            return self._generate_xml_content(updated_data)
    
    def _read_original_xml(self, file_path: Path) -> str:
        """
        Read original XML file content.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            XML content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _update_xml_field(self, root: ET.Element, field_path: str, new_value: Any) -> None:
        """
        Update a specific field in XML tree.
        
        Args:
            root: Root XML element
            field_path: Dot-separated path to field (e.g., "movie.title")
            new_value: New value to set
        """
        path_parts = field_path.split('.')
        current = root
        
        # Navigate to the target element
        for part in path_parts[:-1]:
            found = current.find(part)
            if found is not None:
                current = found
            else:
                # Create missing intermediate elements
                current = ET.SubElement(current, part)
        
        # Update or create the final element
        final_element_name = path_parts[-1]
        target = current.find(final_element_name)
        
        if target is not None:
            target.text = str(new_value)
        else:
            new_element = ET.SubElement(current, final_element_name)
            new_element.text = str(new_value)
    
    def validate_xml_output(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate generated XML content.
        
        Args:
            xml_content: XML content to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'element_count': 0,
            'has_declaration': False
        }
        
        try:
            # Check for XML declaration
            validation_result['has_declaration'] = xml_content.strip().startswith('<?xml')
            
            # Try to parse XML
            root = ET.fromstring(xml_content)
            validation_result['is_valid'] = True
            validation_result['element_count'] = len(list(root.iter()))
            
            # Check for common issues
            if not root.tag:
                validation_result['warnings'].append("Root element has no tag name")
            
            # Check for empty elements
            empty_elements = [elem for elem in root.iter() if not elem.text and not elem.tail and not elem.attrib and not list(elem)]
            if empty_elements:
                validation_result['warnings'].append(f"Found {len(empty_elements)} empty elements")
            
        except ET.ParseError as e:
            validation_result['errors'].append(f"XML parsing error: {str(e)}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
        
        return validation_result
