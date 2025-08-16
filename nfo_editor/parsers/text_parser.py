"""
Plain text parser for NFO files.

This module provides functionality to parse plain text NFO files with various
formats including key-value pairs, INI-style sections, and custom delimited formats.
The parser uses heuristics to detect the structure and convert it to unified NFOData.

Author: NFO Editor Team
"""

import re
import configparser
from io import StringIO
from typing import Union, Dict, Any, Optional, List, Tuple
from pathlib import Path

from .base import BaseNFOParser, NFOData
from ..utils.exceptions import NFOParseError, NFOAccessError


class TextNFOParser(BaseNFOParser):
    """
    Parser for plain text NFO files.
    
    This parser handles various plain text formats including:
    - Key-value pairs with various delimiters (: = |)
    - INI-style sections with [headers]
    - Multi-line values with indentation
    - Custom delimited formats
    - Free-form text with extracted metadata
    
    Attributes:
        supported_extensions (List[str]): Text file extensions this parser supports
        format_name (str): Human-readable name of the format
        auto_detect_format (bool): Whether to auto-detect text structure format
        default_delimiter (str): Default delimiter for key-value pairs
        case_sensitive (bool): Whether field names should be case-sensitive
    """
    
    supported_extensions = ['.nfo', '.txt', '.info', '.meta']
    format_name = "Text"
    
    def __init__(
        self,
        auto_detect_format: bool = True,
        default_delimiter: str = ":",
        case_sensitive: bool = False,
        strip_values: bool = True
    ) -> None:
        """
        Initialize text parser.
        
        Args:
            auto_detect_format: Whether to automatically detect text structure
            default_delimiter: Default delimiter for key-value pairs
            case_sensitive: Whether field names should be case-sensitive
            strip_values: Whether to strip whitespace from values
        """
        self.auto_detect_format = auto_detect_format
        self.default_delimiter = default_delimiter
        self.case_sensitive = case_sensitive
        self.strip_values = strip_values
        
        # Pre-compiled regex patterns for various text formats
        self.patterns = {
            # Key-value patterns with different delimiters
            'colon_kv': re.compile(r'^([^:\n]+):\s*(.*)$', re.MULTILINE),
            'equals_kv': re.compile(r'^([^=\n]+)=\s*(.*)$', re.MULTILINE),
            'pipe_kv': re.compile(r'^([^|\n]+)\|\s*(.*)$', re.MULTILINE),
            'tab_kv': re.compile(r'^([^\t\n]+)\t+(.*)$', re.MULTILINE),
            
            # Section headers
            'ini_section': re.compile(r'^\[([^\]]+)\]$', re.MULTILINE),
            'header_section': re.compile(r'^=+\s*([^=\n]+)\s*=+$', re.MULTILINE),
            'dash_section': re.compile(r'^-+\s*([^-\n]+)\s*-+$', re.MULTILINE),
            
            # Multi-line value patterns
            'indented_continuation': re.compile(r'^(\s{2,})(.+)$', re.MULTILINE),
            
            # Special patterns for common NFO fields
            'title_pattern': re.compile(r'^(title|name|movie|film)\s*[:=]\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'year_pattern': re.compile(r'^(year|date|released?)\s*[:=]\s*(\d{4}).*$', re.IGNORECASE | re.MULTILINE),
            'rating_pattern': re.compile(r'^(rating|score)\s*[:=]\s*([\d.]+).*$', re.IGNORECASE | re.MULTILINE),
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
        
        # Try to read and analyze content structure
        try:
            content = self._read_file_content(file_path, encoding=None)
            
            # Check if content looks like structured text
            return self._is_structured_text(content)
            
        except Exception:
            return False
    
    def parse(self, file_path: Union[str, Path]) -> NFOData:
        """
        Parse a plain text NFO file and return structured data.
        
        Args:
            file_path: Path to the text NFO file to parse
            
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
            
            # Detect and parse structure
            structure_info = self._analyze_structure(content)
            data = self._parse_content_by_structure(content, structure_info)
            
            # Create NFOData object
            nfo_data = NFOData(
                file_path=file_path,
                format_type="text",
                data=data,
                encoding=encoding,
                metadata={
                    'detected_structure': structure_info['primary_format'],
                    'line_count': structure_info['line_count'],
                    'field_count': len(data),
                    'has_sections': structure_info['has_sections'],
                    'primary_delimiter': structure_info['primary_delimiter'],
                    'parser_config': {
                        'auto_detect_format': self.auto_detect_format,
                        'default_delimiter': self.default_delimiter,
                        'case_sensitive': self.case_sensitive
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
                f"Unexpected error during text parsing: {str(e)}",
                file_path=str(file_path),
                format_attempted="Text",
                parse_details=str(e)
            ) from e
    
    def _is_structured_text(self, content: str) -> bool:
        """
        Check if content appears to be structured text suitable for parsing.
        
        Args:
            content: Text content to analyze
            
        Returns:
            True if content appears structured
        """
        if not content.strip():
            return False
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return False  # Need at least 2 lines for structure
        
        # Count lines that look like key-value pairs
        kv_count = 0
        for line in lines:
            if any(delimiter in line for delimiter in [':', '=', '|', '\t']):
                kv_count += 1
        
        # If at least 30% of lines look like key-value pairs, consider it structured
        return (kv_count / len(lines)) >= 0.3
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze the structure of text content to determine parsing strategy.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Dictionary with structure analysis results
        """
        lines = content.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        structure_info = {
            'line_count': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'has_sections': False,
            'primary_format': 'key_value',
            'primary_delimiter': self.default_delimiter,
            'delimiter_counts': {},
            'section_count': 0,
            'indented_lines': 0
        }
        
        # Analyze delimiters
        for delimiter, pattern in [(':', self.patterns['colon_kv']), 
                                   ('=', self.patterns['equals_kv']), 
                                   ('|', self.patterns['pipe_kv']), 
                                   ('\t', self.patterns['tab_kv'])]:
            matches = pattern.findall(content)
            structure_info['delimiter_counts'][delimiter] = len(matches)
        
        # Find primary delimiter
        if structure_info['delimiter_counts']:
            primary_delim = max(structure_info['delimiter_counts'].items(), key=lambda x: x[1])[0]
            if structure_info['delimiter_counts'][primary_delim] > 0:
                structure_info['primary_delimiter'] = primary_delim
        
        # Check for sections
        section_patterns = [
            self.patterns['ini_section'],
            self.patterns['header_section'], 
            self.patterns['dash_section']
        ]
        
        for pattern in section_patterns:
            matches = pattern.findall(content)
            if matches:
                structure_info['has_sections'] = True
                structure_info['section_count'] += len(matches)
                structure_info['primary_format'] = 'sectioned'
                break
        
        # Count indented lines (for multi-line values)
        for line in lines:
            if re.match(r'^\s{2,}', line):
                structure_info['indented_lines'] += 1
        
        return structure_info
    
    def _parse_content_by_structure(self, content: str, structure_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse content based on detected structure.
        
        Args:
            content: Text content to parse
            structure_info: Structure analysis results
            
        Returns:
            Parsed data dictionary
        """
        if structure_info['has_sections']:
            return self._parse_sectioned_content(content, structure_info)
        else:
            return self._parse_key_value_content(content, structure_info)
    
    def _parse_sectioned_content(self, content: str, structure_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse content with section headers.
        
        Args:
            content: Text content to parse
            structure_info: Structure analysis results
            
        Returns:
            Parsed data dictionary with sections
        """
        data = {}
        
        # Try INI-style parsing first
        try:
            config = configparser.ConfigParser(allow_no_value=True)
            config.read_string(content)
            
            for section_name in config.sections():
                section_data = {}
                for key, value in config[section_name].items():
                    clean_key = self._clean_field_name(key)
                    section_data[clean_key] = self._clean_value(value) if value else ""
                data[self._clean_field_name(section_name)] = section_data
            
            if data:
                return data
        
        except configparser.Error:
            pass  # Fall back to manual parsing
        
        # Manual section parsing
        lines = content.split('\n')
        current_section = 'default'
        data[current_section] = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            section_match = None
            for pattern in [self.patterns['ini_section'], 
                           self.patterns['header_section'], 
                           self.patterns['dash_section']]:
                match = pattern.match(line)
                if match:
                    section_match = match
                    break
            
            if section_match:
                current_section = self._clean_field_name(section_match.group(1))
                data[current_section] = {}
            else:
                # Parse as key-value within current section
                delimiter = structure_info['primary_delimiter']
                if delimiter in line:
                    key, value = line.split(delimiter, 1)
                    clean_key = self._clean_field_name(key)
                    clean_value = self._clean_value(value)
                    data[current_section][clean_key] = clean_value
                else:
                    # Add as free-form text
                    if 'text' not in data[current_section]:
                        data[current_section]['text'] = []
                    data[current_section]['text'].append(line)
        
        # Clean up empty sections and convert single-item text lists to strings
        for section_name, section_data in data.items():
            if 'text' in section_data and isinstance(section_data['text'], list):
                if len(section_data['text']) == 1:
                    section_data['text'] = section_data['text'][0]
                elif len(section_data['text']) == 0:
                    del section_data['text']
        
        return {k: v for k, v in data.items() if v}  # Remove empty sections
    
    def _parse_key_value_content(self, content: str, structure_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse content as key-value pairs.
        
        Args:
            content: Text content to parse
            structure_info: Structure analysis results
            
        Returns:
            Parsed data dictionary
        """
        data = {}
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Try to parse as key-value pair
            delimiter = structure_info['primary_delimiter']
            
            if delimiter in line:
                key, value = line.split(delimiter, 1)
                clean_key = self._clean_field_name(key)
                clean_value = self._clean_value(value)
                
                # Check for multi-line values (indented continuation)
                i += 1
                while i < len(lines) and lines[i].startswith('  '):
                    continuation = lines[i].strip()
                    if continuation:
                        clean_value += ' ' + continuation
                    i += 1
                
                data[clean_key] = clean_value
            else:
                # Try alternative delimiters or treat as free text
                parsed = False
                for alt_delimiter in ['=', '|', '\t']:
                    if alt_delimiter in line:
                        key, value = line.split(alt_delimiter, 1)
                        clean_key = self._clean_field_name(key)
                        clean_value = self._clean_value(value)
                        data[clean_key] = clean_value
                        parsed = True
                        break
                
                if not parsed:
                    # Add as free-form text
                    if 'description' not in data:
                        data['description'] = []
                    data['description'].append(line)
                
                i += 1
        
        # Convert single-item description lists to strings
        if 'description' in data and isinstance(data['description'], list):
            if len(data['description']) == 1:
                data['description'] = data['description'][0]
            elif len(data['description']) == 0:
                del data['description']
            else:
                data['description'] = '\n'.join(data['description'])
        
        return data
    
    def _clean_field_name(self, field_name: str) -> str:
        """
        Clean and normalize field names.
        
        Args:
            field_name: Raw field name
            
        Returns:
            Cleaned field name
        """
        if not field_name:
            return 'unknown'
        
        # Remove extra whitespace
        clean_name = field_name.strip()
        
        # Convert to lowercase if not case-sensitive
        if not self.case_sensitive:
            clean_name = clean_name.lower()
        
        # Replace spaces and special characters with underscores
        clean_name = re.sub(r'[^\w]', '_', clean_name)
        
        # Remove multiple underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        return clean_name if clean_name else 'unknown'
    
    def _clean_value(self, value: str) -> str:
        """
        Clean and normalize field values.
        
        Args:
            value: Raw field value
            
        Returns:
            Cleaned field value
        """
        if value is None:
            return ""
        
        clean_value = str(value)
        
        if self.strip_values:
            clean_value = clean_value.strip()
        
        return clean_value
    
    def get_common_fields(self, nfo_data: NFOData) -> Dict[str, Any]:
        """
        Extract commonly used fields from text NFO data.
        
        Args:
            nfo_data: Parsed NFO data
            
        Returns:
            Dictionary with commonly used field mappings
        """
        common_fields = {}
        data = nfo_data.data
        
        # Flatten sectioned data for field search
        flat_data = {}
        if nfo_data.metadata.get('has_sections', False):
            for section_name, section_data in data.items():
                if isinstance(section_data, dict):
                    flat_data.update(section_data)
                    # Also add prefixed versions
                    for key, value in section_data.items():
                        flat_data[f"{section_name}_{key}"] = value
        else:
            flat_data = data
        
        # Common field mappings for text formats
        field_mappings = [
            ('title', ['title', 'name', 'movie', 'film', 'show', 'album']),
            ('plot', ['plot', 'summary', 'description', 'synopsis', 'desc']),
            ('year', ['year', 'date', 'released', 'release_year']),
            ('genre', ['genre', 'genres', 'category', 'type']),
            ('rating', ['rating', 'score', 'imdb', 'stars']),
            ('runtime', ['runtime', 'duration', 'length', 'time']),
            ('director', ['director', 'directors', 'directed_by']),
            ('cast', ['cast', 'actors', 'starring', 'stars']),
            ('studio', ['studio', 'studios', 'producer', 'production']),
            ('artist', ['artist', 'performer', 'musician']),
            ('track', ['track', 'track_number', 'song']),
            ('season', ['season', 'season_number']),
            ('episode', ['episode', 'episode_number']),
        ]
        
        for common_name, possible_keys in field_mappings:
            value = self._find_field_value(flat_data, possible_keys)
            if value is not None and value != "":
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
        # Direct key matches
        for key in possible_keys:
            if key in data:
                return data[key]
        
        # Case-insensitive and fuzzy matches
        for key in possible_keys:
            for data_key, value in data.items():
                if isinstance(data_key, str):
                    # Exact case-insensitive match
                    if data_key.lower() == key.lower():
                        return value
                    
                    # Contains match (for compound keys)
                    if key.lower() in data_key.lower() or data_key.lower() in key.lower():
                        return value
        
        return None
    
    def detect_text_format(self, content: str) -> str:
        """
        Detect the specific format of text content.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Format identifier string
        """
        structure_info = self._analyze_structure(content)
        
        if structure_info['has_sections']:
            return "sectioned_text"
        elif structure_info['primary_delimiter'] == ':':
            return "colon_delimited"
        elif structure_info['primary_delimiter'] == '=':
            return "equals_delimited"
        elif structure_info['primary_delimiter'] == '|':
            return "pipe_delimited"
        elif structure_info['primary_delimiter'] == '\t':
            return "tab_delimited"
        else:
            return "free_form_text"
