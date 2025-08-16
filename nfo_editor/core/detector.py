"""
Format detection logic for NFO files.

This module provides functionality to automatically detect the format of NFO files
(XML, JSON, plain text, etc.) based on file content analysis.

Author: NFO Editor Team
"""

import re
import json
import xml.etree.ElementTree as ET
from typing import Union, Optional, List, Dict, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from ..utils.exceptions import NFOAccessError, NFOFormatError


class NFOFormat(Enum):
    """
    Enumeration of supported NFO file formats.
    
    Each format has an associated string value that can be used
    for identification and logging purposes.
    """
    XML = "xml"
    JSON = "json"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class FormatDetectionResult:
    """
    Result of format detection analysis.
    
    Attributes:
        format_type (NFOFormat): Detected format type
        confidence (float): Confidence score (0.0 to 1.0)
        details (Dict[str, Any]): Additional details about the detection
        fallback_formats (List[NFOFormat]): Alternative formats to try if primary fails
        encoding (str): Detected character encoding
    """
    format_type: NFOFormat
    confidence: float
    details: Dict[str, Any]
    fallback_formats: List[NFOFormat] = None
    encoding: str = "utf-8"
    
    def __post_init__(self) -> None:
        """Initialize default fallback formats if not provided."""
        if self.fallback_formats is None:
            self.fallback_formats = []


class NFOFormatDetector:
    """
    Detector for automatically identifying NFO file formats.
    
    This class analyzes file content using various heuristics to determine
    the most likely format of an NFO file. It supports XML, JSON, and plain
    text formats with configurable detection parameters.
    
    Attributes:
        min_confidence_threshold (float): Minimum confidence required for detection
        enable_content_sniffing (bool): Whether to analyze file content beyond headers
        max_sample_size (int): Maximum bytes to read for format detection
    """
    
    def __init__(
        self,
        min_confidence_threshold: float = 0.7,
        enable_content_sniffing: bool = True,
        max_sample_size: int = 8192
    ) -> None:
        """
        Initialize format detector.
        
        Args:
            min_confidence_threshold: Minimum confidence required for detection
            enable_content_sniffing: Whether to analyze file content beyond headers
            max_sample_size: Maximum bytes to read for format detection
        """
        self.min_confidence_threshold = min_confidence_threshold
        self.enable_content_sniffing = enable_content_sniffing
        self.max_sample_size = max_sample_size
        
        # Pre-compiled regex patterns for efficient matching
        self._xml_patterns = [
            re.compile(r'^\s*<\?xml\s+version\s*=', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*<[a-zA-Z][^>]*>', re.MULTILINE),
            re.compile(r'</(movie|tvshow|episodedetails|album|artist|song)', re.IGNORECASE),
            re.compile(r'<(title|plot|genre|year|rating|director)', re.IGNORECASE),
        ]
        
        self._json_patterns = [
            re.compile(r'^\s*\{', re.MULTILINE),
            re.compile(r'^\s*\[', re.MULTILINE),
            re.compile(r'"(title|plot|genre|year|rating)":\s*"', re.IGNORECASE),
        ]
        
        self._text_patterns = [
            re.compile(r'^[a-zA-Z][^:=]*[:=]\s*[^\r\n]+', re.MULTILINE),
            re.compile(r'^\[[^\]]+\]\s*$', re.MULTILINE),  # [Section] headers
            re.compile(r'^(Title|Genre|Year|Rating|Plot)\s*[:=]', re.IGNORECASE | re.MULTILINE),
        ]
    
    def detect_format(self, file_path: Union[str, Path]) -> FormatDetectionResult:
        """
        Detect the format of an NFO file.
        
        Args:
            file_path: Path to the NFO file to analyze
            
        Returns:
            FormatDetectionResult with detected format and confidence
            
        Raises:
            NFOAccessError: If file cannot be read
            NFOFormatError: If format cannot be determined
        """
        file_path = Path(file_path)
        
        # Read file content
        content, encoding = self._read_file_sample(file_path)
        
        if not content.strip():
            raise NFOFormatError(
                "File is empty or contains only whitespace",
                file_path=str(file_path),
                detected_format="empty"
            )
        
        # Try different detection methods
        detection_results = []
        
        # Method 1: XML detection
        xml_result = self._detect_xml_format(content, file_path)
        if xml_result:
            detection_results.append(xml_result)
        
        # Method 2: JSON detection  
        json_result = self._detect_json_format(content, file_path)
        if json_result:
            detection_results.append(json_result)
        
        # Method 3: Plain text detection
        text_result = self._detect_text_format(content, file_path)
        if text_result:
            detection_results.append(text_result)
        
        # Select best result
        if not detection_results:
            return FormatDetectionResult(
                format_type=NFOFormat.UNKNOWN,
                confidence=0.0,
                details={"error": "No format patterns matched"},
                encoding=encoding
            )
        
        # Sort by confidence and return the best match
        best_result = max(detection_results, key=lambda r: r.confidence)
        best_result.encoding = encoding
        
        # Set fallback formats
        other_formats = [r.format_type for r in detection_results if r != best_result]
        best_result.fallback_formats = other_formats
        
        return best_result
    
    def _read_file_sample(self, file_path: Path) -> tuple[str, str]:
        """
        Read a sample of the file content for analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (content, encoding)
            
        Raises:
            NFOAccessError: If file cannot be read
        """
        try:
            # Try to detect encoding first
            encoding = self._detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read(self.max_sample_size)
                
            return content, encoding
            
        except Exception as e:
            raise NFOAccessError(
                f"Cannot read file for format detection: {str(e)}",
                file_path=str(file_path),
                access_mode="read",
                system_error=str(e)
            ) from e
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        try:
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(min(self.max_sample_size, 1024))
            
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') or 'utf-8'
            
        except Exception:
            return 'utf-8'  # Fallback to utf-8
    
    def _detect_xml_format(self, content: str, file_path: Path) -> Optional[FormatDetectionResult]:
        """
        Attempt to detect XML format.
        
        Args:
            content: File content to analyze
            file_path: Path to the file (for error reporting)
            
        Returns:
            FormatDetectionResult if XML is detected, None otherwise
        """
        confidence = 0.0
        details = {}
        
        # Check for XML declaration
        if self._xml_patterns[0].search(content):
            confidence += 0.3
            details["has_xml_declaration"] = True
        
        # Check for opening XML tags
        if self._xml_patterns[1].search(content):
            confidence += 0.2
            details["has_opening_tags"] = True
        
        # Check for common NFO XML elements
        common_elements = self._xml_patterns[2].findall(content)
        if common_elements:
            confidence += min(0.3, len(common_elements) * 0.1)
            details["common_elements"] = common_elements
        
        # Check for typical NFO fields in XML
        field_matches = self._xml_patterns[3].findall(content)
        if field_matches:
            confidence += min(0.2, len(field_matches) * 0.05)
            details["nfo_fields"] = field_matches
        
        # Try to parse as XML to verify structure
        if confidence > 0.4:
            try:
                ET.fromstring(content)
                confidence += 0.2
                details["valid_xml_structure"] = True
            except ET.ParseError as e:
                confidence *= 0.5  # Reduce confidence if parsing fails
                details["xml_parse_error"] = str(e)
        
        if confidence >= self.min_confidence_threshold * 0.5:  # Lower threshold for XML
            return FormatDetectionResult(
                format_type=NFOFormat.XML,
                confidence=min(confidence, 1.0),
                details=details
            )
        
        return None
    
    def _detect_json_format(self, content: str, file_path: Path) -> Optional[FormatDetectionResult]:
        """
        Attempt to detect JSON format.
        
        Args:
            content: File content to analyze
            file_path: Path to the file (for error reporting)
            
        Returns:
            FormatDetectionResult if JSON is detected, None otherwise
        """
        confidence = 0.0
        details = {}
        
        # Check for JSON object/array opening
        if self._json_patterns[0].search(content) or self._json_patterns[1].search(content):
            confidence += 0.3
            details["has_json_structure"] = True
        
        # Check for common NFO fields in JSON format
        field_matches = self._json_patterns[2].findall(content)
        if field_matches:
            confidence += min(0.4, len(field_matches) * 0.1)
            details["nfo_fields"] = field_matches
        
        # Try to parse as JSON to verify structure
        if confidence > 0.2:
            try:
                json.loads(content)
                confidence += 0.4
                details["valid_json_structure"] = True
            except json.JSONDecodeError as e:
                confidence *= 0.3  # Significantly reduce confidence if parsing fails
                details["json_parse_error"] = str(e)
        
        if confidence >= self.min_confidence_threshold * 0.7:  # Standard threshold for JSON
            return FormatDetectionResult(
                format_type=NFOFormat.JSON,
                confidence=min(confidence, 1.0),
                details=details
            )
        
        return None
    
    def _detect_text_format(self, content: str, file_path: Path) -> Optional[FormatDetectionResult]:
        """
        Attempt to detect plain text format.
        
        Args:
            content: File content to analyze
            file_path: Path to the file (for error reporting)
            
        Returns:
            FormatDetectionResult if text format is detected, None otherwise
        """
        confidence = 0.0
        details = {}
        
        # Check for key-value pairs
        kv_matches = self._text_patterns[0].findall(content)
        if kv_matches:
            confidence += min(0.4, len(kv_matches) * 0.05)
            details["key_value_pairs"] = len(kv_matches)
        
        # Check for section headers
        section_matches = self._text_patterns[1].findall(content)
        if section_matches:
            confidence += min(0.2, len(section_matches) * 0.1)
            details["section_headers"] = section_matches
        
        # Check for common NFO field names
        nfo_field_matches = self._text_patterns[2].findall(content)
        if nfo_field_matches:
            confidence += min(0.3, len(nfo_field_matches) * 0.1)
            details["nfo_field_names"] = nfo_field_matches
        
        # Boost confidence if content looks like structured text
        lines = content.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if non_empty_lines:
            # Check line structure consistency
            colon_lines = sum(1 for line in non_empty_lines if ':' in line)
            equals_lines = sum(1 for line in non_empty_lines if '=' in line)
            
            structured_ratio = (colon_lines + equals_lines) / len(non_empty_lines)
            
            if structured_ratio > 0.5:
                confidence += 0.2
                details["structured_ratio"] = structured_ratio
        
        # Plain text is always a fallback option
        confidence = max(confidence, 0.1)  # Minimum confidence for text format
        
        return FormatDetectionResult(
            format_type=NFOFormat.TEXT,
            confidence=min(confidence, 1.0),
            details=details
        )
    
    def detect_multiple_files(
        self, 
        file_paths: List[Union[str, Path]]
    ) -> Dict[str, FormatDetectionResult]:
        """
        Detect formats for multiple files.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            Dictionary mapping file paths to detection results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                result = self.detect_format(file_path)
                results[str(file_path)] = result
            except Exception as e:
                # Create error result for failed detections
                results[str(file_path)] = FormatDetectionResult(
                    format_type=NFOFormat.UNKNOWN,
                    confidence=0.0,
                    details={"error": str(e)}
                )
        
        return results
    
    def get_format_statistics(
        self, 
        file_paths: List[Union[str, Path]]
    ) -> Dict[str, Any]:
        """
        Get statistics about format distribution across multiple files.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            Dictionary with format statistics
        """
        results = self.detect_multiple_files(file_paths)
        
        format_counts = {}
        confidence_scores = []
        errors = []
        
        for path, result in results.items():
            format_name = result.format_type.value
            format_counts[format_name] = format_counts.get(format_name, 0) + 1
            
            if result.format_type != NFOFormat.UNKNOWN:
                confidence_scores.append(result.confidence)
            
            if "error" in result.details:
                errors.append({"file": path, "error": result.details["error"]})
        
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores else 0.0
        )
        
        return {
            "total_files": len(file_paths),
            "format_distribution": format_counts,
            "average_confidence": avg_confidence,
            "detection_errors": errors,
            "successful_detections": len(file_paths) - len(errors)
        }
