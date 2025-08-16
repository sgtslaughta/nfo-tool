"""
JSON parser for NFO files.

This module provides functionality to parse JSON-formatted NFO files, which
provide a structured and easily readable format for media metadata. The parser
handles various JSON structures and converts them to the unified NFOData format.

Author: NFO Editor Team
"""

import json
from typing import Union, Dict, Any, Optional, List
from pathlib import Path

from .base import BaseNFOParser, NFOData
from ..utils.exceptions import NFOParseError, NFOAccessError


class JSONNFOParser(BaseNFOParser):
    """
    Parser for JSON-formatted NFO files.
    
    This parser handles JSON NFO files with flexible schema support. It can parse
    both flat key-value structures and nested object hierarchies, making it suitable
    for various JSON-based metadata formats.
    
    Attributes:
        supported_extensions (List[str]): JSON file extensions this parser supports
        format_name (str): Human-readable name of the format
        strict_mode (bool): Whether to enforce strict JSON parsing
        allow_comments (bool): Whether to allow JSON with comments (JSON5 style)
    """
    
    supported_extensions = ['.json', '.nfo']
    format_name = "JSON"
    
    def __init__(
        self,
        strict_mode: bool = False,
        allow_comments: bool = True
    ) -> None:
        """
        Initialize JSON parser.
        
        Args:
            strict_mode: Whether to enforce strict JSON parsing (no comments, trailing commas)
            allow_comments: Whether to allow JSON with comments and relaxed syntax
        """
        self.strict_mode = strict_mode
        self.allow_comments = allow_comments
    
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
        
        # Try to parse the content to check if it's valid JSON
        try:
            content = self._read_file_content(file_path, encoding=None)
            
            # Quick check for JSON-like content
            content = content.strip()
            if not (content.startswith('{') or content.startswith('[')):
                return False
            
            # Try to parse as JSON
            self._parse_json_content(content)
            return True
            
        except Exception:
            return False
    
    def parse(self, file_path: Union[str, Path]) -> NFOData:
        """
        Parse a JSON NFO file and return structured data.
        
        Args:
            file_path: Path to the JSON NFO file to parse
            
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
            
            # Parse JSON
            try:
                data = self._parse_json_content(content)
            except json.JSONDecodeError as e:
                raise NFOParseError(
                    f"Invalid JSON structure: {str(e)}",
                    file_path=str(file_path),
                    format_attempted="JSON",
                    parse_details=f"Line {e.lineno}, Column {e.colno}: {e.msg}"
                ) from e
            
            # Ensure data is a dictionary (convert if it's a list)
            if isinstance(data, list):
                data = {'items': data}
            elif not isinstance(data, dict):
                data = {'value': data}
            
            # Create NFOData object
            nfo_data = NFOData(
                file_path=file_path,
                format_type="json",
                data=data,
                encoding=encoding,
                metadata={
                    'original_structure': type(data).__name__,
                    'total_keys': self._count_keys(data),
                    'max_depth': self._calculate_depth(data),
                    'parser_config': {
                        'strict_mode': self.strict_mode,
                        'allow_comments': self.allow_comments
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
                f"Unexpected error during JSON parsing: {str(e)}",
                file_path=str(file_path),
                format_attempted="JSON",
                parse_details=str(e)
            ) from e
    
    def _parse_json_content(self, content: str) -> Any:
        """
        Parse JSON content with support for relaxed syntax if configured.
        
        Args:
            content: JSON content string to parse
            
        Returns:
            Parsed JSON data
            
        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        if self.strict_mode:
            # Use strict JSON parsing
            return json.loads(content)
        else:
            # Try standard JSON first
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if self.allow_comments:
                    # Try parsing with comment removal
                    cleaned_content = self._remove_json_comments(content)
                    return json.loads(cleaned_content)
                else:
                    raise
    
    def _remove_json_comments(self, content: str) -> str:
        """
        Remove comments from JSON content to allow for relaxed parsing.
        
        This method removes single-line comments (//) and multi-line comments (/* */)
        while preserving strings that might contain these patterns.
        
        Args:
            content: JSON content with comments
            
        Returns:
            JSON content with comments removed
        """
        import re
        
        # Pattern to match comments while avoiding strings
        # This is a simplified approach - a more robust solution would use a proper lexer
        
        lines = content.split('\n')
        cleaned_lines = []
        
        in_multiline_comment = False
        
        for line in lines:
            cleaned_line = ""
            i = 0
            in_string = False
            escape_next = False
            
            while i < len(line):
                char = line[i]
                
                if escape_next:
                    cleaned_line += char
                    escape_next = False
                    i += 1
                    continue
                
                if char == '\\' and in_string:
                    cleaned_line += char
                    escape_next = True
                    i += 1
                    continue
                
                if char == '"' and not in_multiline_comment:
                    in_string = not in_string
                    cleaned_line += char
                elif in_string:
                    cleaned_line += char
                elif in_multiline_comment:
                    if char == '*' and i + 1 < len(line) and line[i + 1] == '/':
                        in_multiline_comment = False
                        i += 1  # Skip the '/'
                elif char == '/' and i + 1 < len(line):
                    if line[i + 1] == '/':
                        # Single-line comment - ignore rest of line
                        break
                    elif line[i + 1] == '*':
                        # Multi-line comment start
                        in_multiline_comment = True
                        i += 1  # Skip the '*'
                    else:
                        cleaned_line += char
                else:
                    cleaned_line += char
                
                i += 1
            
            if not in_multiline_comment:
                cleaned_lines.append(cleaned_line.rstrip())
        
        return '\n'.join(cleaned_lines)
    
    def _count_keys(self, data: Dict[str, Any]) -> int:
        """
        Count total number of keys in a nested dictionary.
        
        Args:
            data: Dictionary to count keys in
            
        Returns:
            Total number of keys
        """
        if not isinstance(data, dict):
            return 0
        
        count = len(data)
        
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_keys(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        count += self._count_keys(item)
        
        return count
    
    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """
        Calculate the maximum depth of a nested data structure.
        
        Args:
            data: Data structure to analyze
            current_depth: Current depth level
            
        Returns:
            Maximum depth of the structure
        """
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(
                self._calculate_depth(value, current_depth + 1)
                for value in data.values()
            )
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(
                self._calculate_depth(item, current_depth + 1)
                for item in data
            )
        else:
            return current_depth
    
    def get_common_fields(self, nfo_data: NFOData) -> Dict[str, Any]:
        """
        Extract commonly used fields from JSON NFO data.
        
        This method identifies and extracts standard media metadata fields
        that are commonly found in JSON NFO files.
        
        Args:
            nfo_data: Parsed NFO data
            
        Returns:
            Dictionary with commonly used field mappings
        """
        common_fields = {}
        data = nfo_data.data
        
        # Common field mappings for JSON structures
        field_mappings = [
            # Movie/TV show fields
            ('title', ['title', 'name', 'originalTitle', 'original_title']),
            ('plot', ['plot', 'summary', 'description', 'overview', 'synopsis']),
            ('year', ['year', 'releaseYear', 'release_year', 'premiered']),
            ('genre', ['genre', 'genres']),
            ('rating', ['rating', 'imdbRating', 'imdb_rating', 'tmdbRating', 'tmdb_rating']),
            ('runtime', ['runtime', 'duration', 'length']),
            ('director', ['director', 'directors']),
            ('cast', ['cast', 'actors', 'actor']),
            ('studio', ['studio', 'studios', 'distributor', 'production_company']),
            ('tagline', ['tagline', 'slogan']),
            
            # Music fields
            ('artist', ['artist', 'albumArtist', 'album_artist', 'performer']),
            ('album', ['album', 'albumName', 'album_name']),
            ('track', ['track', 'trackNumber', 'track_number']),
            ('discnumber', ['discNumber', 'disc_number', 'disc']),
            
            # Episode fields
            ('season', ['season', 'seasonNumber', 'season_number']),
            ('episode', ['episode', 'episodeNumber', 'episode_number']),
            ('showtitle', ['showTitle', 'show_title', 'seriesName', 'series_name']),
            
            # General metadata
            ('dateadded', ['dateAdded', 'date_added', 'added', 'created']),
            ('lastplayed', ['lastPlayed', 'last_played', 'viewed']),
            ('playcount', ['playCount', 'play_count', 'timesViewed', 'times_viewed']),
        ]
        
        for common_name, possible_keys in field_mappings:
            value = self._find_field_value(data, possible_keys)
            if value is not None:
                common_fields[common_name] = value
        
        return common_fields
    
    def _find_field_value(self, data: Dict[str, Any], possible_keys: List[str]) -> Any:
        """
        Find a field value using multiple possible key names.
        
        This method searches through the data structure using various naming conventions
        commonly found in JSON NFO files (camelCase, snake_case, etc.).
        
        Args:
            data: Dictionary to search in
            possible_keys: List of possible key names to try
            
        Returns:
            Found value or None if not found
        """
        # First, try direct key matches
        for key in possible_keys:
            if key in data:
                return data[key]
        
        # Then try case-insensitive matches
        data_keys_lower = {k.lower(): k for k in data.keys() if isinstance(k, str)}
        
        for key in possible_keys:
            key_lower = key.lower()
            if key_lower in data_keys_lower:
                actual_key = data_keys_lower[key_lower]
                return data[actual_key]
        
        # Finally, try nested search for common patterns
        return self._deep_search_field(data, possible_keys)
    
    def _deep_search_field(self, data: Any, possible_keys: List[str], max_depth: int = 2) -> Any:
        """
        Perform a deep search for field values in nested structures.
        
        Args:
            data: Data structure to search in
            possible_keys: List of possible key names
            max_depth: Maximum depth to search
            
        Returns:
            Found value or None if not found
        """
        if max_depth <= 0:
            return None
        
        if isinstance(data, dict):
            # Search in current level
            for key in possible_keys:
                if key in data:
                    return data[key]
            
            # Search in nested dictionaries
            for value in data.values():
                result = self._deep_search_field(value, possible_keys, max_depth - 1)
                if result is not None:
                    return result
        
        elif isinstance(data, list):
            # Search in list items
            for item in data:
                result = self._deep_search_field(item, possible_keys, max_depth - 1)
                if result is not None:
                    return result
        
        return None
    
    def validate_json_structure(self, nfo_data: NFOData) -> Dict[str, Any]:
        """
        Validate the JSON structure and provide analysis.
        
        Args:
            nfo_data: NFOData object to validate
            
        Returns:
            Dictionary with validation results and recommendations
        """
        data = nfo_data.data
        
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'recommendations': [],
            'structure_analysis': {}
        }
        
        # Analyze structure
        validation_result['structure_analysis'] = {
            'total_keys': self._count_keys(data),
            'max_depth': self._calculate_depth(data),
            'has_arrays': self._contains_arrays(data),
            'has_nested_objects': self._contains_nested_objects(data),
            'empty_values': self._count_empty_values(data)
        }
        
        # Check for potential issues
        if validation_result['structure_analysis']['max_depth'] > 5:
            validation_result['warnings'].append(
                f"Deep nesting detected (depth: {validation_result['structure_analysis']['max_depth']})"
            )
        
        if validation_result['structure_analysis']['empty_values'] > 0:
            validation_result['warnings'].append(
                f"Found {validation_result['structure_analysis']['empty_values']} empty values"
            )
        
        # Provide recommendations
        common_fields = self.get_common_fields(nfo_data)
        if len(common_fields) < 3:
            validation_result['recommendations'].append(
                "Consider adding more standard metadata fields (title, plot, year, etc.)"
            )
        
        return validation_result
    
    def _contains_arrays(self, data: Any) -> bool:
        """Check if data structure contains arrays."""
        if isinstance(data, list):
            return True
        elif isinstance(data, dict):
            return any(self._contains_arrays(value) for value in data.values())
        return False
    
    def _contains_nested_objects(self, data: Any) -> bool:
        """Check if data structure contains nested objects."""
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, dict):
                    return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            return True
        return False
    
    def _count_empty_values(self, data: Any) -> int:
        """Count empty or null values in the data structure."""
        count = 0
        
        if isinstance(data, dict):
            for value in data.values():
                if value is None or value == "" or value == []:
                    count += 1
                else:
                    count += self._count_empty_values(value)
        elif isinstance(data, list):
            for item in data:
                if item is None or item == "" or item == []:
                    count += 1
                else:
                    count += self._count_empty_values(item)
        
        return count
