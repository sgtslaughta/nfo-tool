"""
XML parser for NFO files.

This module provides functionality to parse XML-formatted NFO files, which are
commonly used for media metadata (movies, TV shows, music, etc.). The parser
handles various XML structures and converts them to the unified NFOData format.

Author: NFO Editor Team
"""

import xml.etree.ElementTree as ET
from typing import Union, Dict, Any, Optional, List
from pathlib import Path

from .base import BaseNFOParser, NFOData
from ..utils.exceptions import NFOParseError, NFOAccessError


class XMLNFOParser(BaseNFOParser):
    """
    Parser for XML-formatted NFO files.
    
    This parser handles various XML NFO formats including Kodi/XBMC media center
    formats for movies, TV shows, episodes, music albums, and custom XML structures.
    It preserves the hierarchical structure while providing easy field access.
    
    Attributes:
        supported_extensions (List[str]): XML file extensions this parser supports
        format_name (str): Human-readable name of the format
        preserve_namespaces (bool): Whether to preserve XML namespaces
        convert_types (bool): Whether to convert string values to appropriate types
    """
    
    supported_extensions = ['.xml', '.nfo']
    format_name = "XML"
    
    def __init__(
        self,
        preserve_namespaces: bool = False,
        convert_types: bool = True
    ) -> None:
        """
        Initialize XML parser.
        
        Args:
            preserve_namespaces: Whether to preserve XML namespaces in field names
            convert_types: Whether to convert string values to appropriate types
        """
        self.preserve_namespaces = preserve_namespaces
        self.convert_types = convert_types
        
        # Common XML namespace prefixes for NFO files
        self.common_namespaces = {
            'kodi': 'http://kodi.tv/nfo',
            'xbmc': 'http://xbmc.org/nfo',
            'media': 'http://mediainfo.tv/nfo',
        }
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this parser can handle the file, False otherwise
        """
        file_path = Path(file_path)
        
        # Check file extension
        if file_path.suffix.lower() not in [ext.lower() for ext in self.supported_extensions]:
            return False
        
        # Try to parse the first few lines to check if it's valid XML
        try:
            content = self._read_file_content(file_path, encoding=None)
            
            # Quick check for XML-like content
            if not content.strip().startswith('<'):
                return False
            
            # Try to parse first element to verify XML structure
            # Only read first 1000 characters for quick validation
            sample = content[:1000]
            if '<' in sample and '>' in sample:
                # Try to find the first complete tag
                try:
                    ET.fromstring(content)
                    return True
                except ET.ParseError:
                    return False
            
            return False
            
        except Exception:
            return False
    
    def parse(self, file_path: Union[str, Path]) -> NFOData:
        """
        Parse an XML NFO file and return structured data.
        
        Args:
            file_path: Path to the XML NFO file to parse
            
        Returns:
            NFOData object containing the parsed information
            
        Raises:
            NFOParseError: If parsing fails
            NFOAccessError: If file cannot be read
        """
        file_path = Path(file_path)
        
        try:
            # Read file content
            encoding = self._detect_encoding(file_path)
            content = self._read_file_content(file_path, encoding=encoding)
            
            # Parse XML
            try:
                root = ET.fromstring(content)
            except ET.ParseError as e:
                raise NFOParseError(
                    f"Invalid XML structure: {str(e)}",
                    file_path=str(file_path),
                    format_attempted="XML",
                    parse_details=str(e)
                ) from e
            
            # Convert XML to dictionary structure
            data = self._xml_to_dict(root)
            
            # Create NFOData object
            nfo_data = NFOData(
                file_path=file_path,
                format_type="xml",
                data=data,
                encoding=encoding,
                metadata={
                    'root_element': root.tag,
                    'xml_namespaces': self._extract_namespaces(root),
                    'element_count': self._count_elements(root),
                    'parser_config': {
                        'preserve_namespaces': self.preserve_namespaces,
                        'convert_types': self.convert_types
                    }
                }
            )
            
            return nfo_data
            
        except NFOParseError:
            raise
        except NFOAccessError:
            raise
        except Exception as e:
            raise NFOParseError(
                f"Unexpected error during XML parsing: {str(e)}",
                file_path=str(file_path),
                format_attempted="XML",
                parse_details=str(e)
            ) from e
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Convert XML element tree to dictionary structure.
        
        Args:
            element: XML element to convert
            
        Returns:
            Dictionary representation of the XML structure
        """
        result = {}
        
        # Handle element tag name (remove namespace if configured)
        tag = element.tag
        if not self.preserve_namespaces and '}' in tag:
            tag = tag.split('}', 1)[1]  # Remove namespace
        
        # Handle element text content
        text = element.text.strip() if element.text else ""
        
        # Handle element attributes
        attributes = {}
        for attr_name, attr_value in element.attrib.items():
            # Remove namespace from attribute names if configured
            clean_attr_name = attr_name
            if not self.preserve_namespaces and '}' in attr_name:
                clean_attr_name = attr_name.split('}', 1)[1]
            
            attributes[f"@{clean_attr_name}"] = self._convert_value(attr_value)
        
        # Handle child elements
        children = {}
        child_groups = {}  # Track multiple children with same tag
        
        for child in element:
            child_tag = child.tag
            if not self.preserve_namespaces and '}' in child_tag:
                child_tag = child_tag.split('}', 1)[1]
            
            child_data = self._xml_to_dict(child)
            
            # Handle multiple children with the same tag
            if child_tag in children:
                # We've seen this tag before
                existing_value = children[child_tag]
                if isinstance(existing_value, list):
                    # Already a list, just append
                    existing_value.append(child_data)
                else:
                    # Convert to list with both old and new values
                    children[child_tag] = [existing_value, child_data]
                child_groups[child_tag] = child_groups.get(child_tag, 1) + 1
            else:
                # First occurrence of this tag
                children[child_tag] = child_data
                child_groups[child_tag] = 1
        
        # Build final result
        if text and not children and not attributes:
            # Simple text element
            return self._convert_value(text)
        elif not text and not attributes and len(children) == 1:
            # Single child element - flatten structure
            child_key, child_value = next(iter(children.items()))
            if isinstance(child_value, dict) and len(child_value) == 1:
                return child_value
        
        # Complex element - build dictionary
        if text:
            result['#text'] = self._convert_value(text)
        
        if attributes:
            result.update(attributes)
        
        if children:
            result.update(children)
        
        return result
    
    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate type if type conversion is enabled.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value or original string
        """
        if not self.convert_types:
            return value
        
        # Try to convert to appropriate types
        value = value.strip()
        
        if not value:
            return value
        
        # Boolean values
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # Numeric values
        try:
            # Try integer first
            if '.' not in value:
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass
        
        # Return as string if no conversion applies
        return value
    
    def _extract_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """
        Extract XML namespaces from the root element.
        
        Args:
            root: Root XML element
            
        Returns:
            Dictionary mapping namespace prefixes to URIs
        """
        namespaces = {}
        
        # Extract from root element attributes
        for attr_name, attr_value in root.attrib.items():
            if attr_name.startswith('xmlns'):
                if ':' in attr_name:
                    prefix = attr_name.split(':', 1)[1]
                    namespaces[prefix] = attr_value
                else:
                    namespaces['default'] = attr_value
        
        return namespaces
    
    def _count_elements(self, root: ET.Element) -> int:
        """
        Count total number of elements in the XML tree.
        
        Args:
            root: Root XML element
            
        Returns:
            Total count of elements
        """
        count = 1  # Count root element
        
        for child in root:
            count += self._count_elements(child)
        
        return count
    
    def get_common_fields(self, nfo_data: NFOData) -> Dict[str, Any]:
        """
        Extract commonly used fields from XML NFO data.
        
        This method identifies and extracts standard media metadata fields
        that are commonly found in XML NFO files.
        
        Args:
            nfo_data: Parsed NFO data
            
        Returns:
            Dictionary with commonly used field mappings
        """
        common_fields = {}
        data = nfo_data.data
        
        # Common field mappings for different XML structures
        field_mappings = [
            # Movie/TV show fields
            ('title', ['title', 'name', 'originaltitle']),
            ('plot', ['plot', 'summary', 'description', 'overview']),
            ('year', ['year', 'premiered', 'releasedate']),
            ('genre', ['genre', 'genres']),
            ('rating', ['rating', 'imdb_rating', 'tmdb_rating']),
            ('runtime', ['runtime', 'duration']),
            ('director', ['director', 'directors']),
            ('cast', ['actor', 'actors', 'cast']),
            ('studio', ['studio', 'studios', 'distributor']),
            ('tagline', ['tagline', 'slogan']),
            
            # Music fields
            ('artist', ['artist', 'albumartist', 'performer']),
            ('album', ['album', 'title']),
            ('track', ['track', 'tracknumber']),
            ('discnumber', ['discnumber', 'disc']),
            
            # Episode fields
            ('season', ['season', 'seasonnumber']),
            ('episode', ['episode', 'episodenumber']),
            ('showtitle', ['showtitle', 'seriesname']),
            
            # General metadata
            ('dateadded', ['dateadded', 'added', 'created']),
            ('lastplayed', ['lastplayed', 'viewed']),
            ('playcount', ['playcount', 'timesviewed']),
        ]
        
        for common_name, possible_keys in field_mappings:
            value = self._find_field_value(data, possible_keys)
            if value is not None:
                common_fields[common_name] = value
        
        return common_fields
    
    def _find_field_value(self, data: Dict[str, Any], possible_keys: List[str]) -> Any:
        """
        Find a field value using multiple possible key names.
        
        Args:
            data: Dictionary to search in
            possible_keys: List of possible key names to try
            
        Returns:
            Found value or None if not found
        """
        for key in possible_keys:
            # Try exact match
            if key in data:
                return data[key]
            
            # Try case-insensitive match
            for actual_key, value in data.items():
                if isinstance(actual_key, str) and actual_key.lower() == key.lower():
                    return value
        
        return None
