"""
Custom exception classes for NFO file handling.

This module defines all custom exceptions used throughout the NFO editor library.
Each exception provides specific error information for different failure modes.

Author: NFO Editor Team
"""

from typing import Optional, Any


class NFOError(Exception):
    """
    Base exception class for all NFO-related errors.
    
    All other NFO exceptions inherit from this base class, allowing
    users to catch all NFO-specific errors with a single except clause.
    
    Attributes:
        message (str): Human-readable error description
        file_path (Optional[str]): Path to the file that caused the error
        details (Optional[dict]): Additional error context information
    """

    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None, 
        details: Optional[dict] = None
    ) -> None:
        """
        Initialize NFO error.
        
        Args:
            message: Human-readable error description
            file_path: Optional path to the file that caused the error
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.file_path = file_path
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return formatted error message."""
        base_msg = self.message
        if self.file_path:
            base_msg += f" (file: {self.file_path})"
        return base_msg


class NFOParseError(NFOError):
    """
    Raised when an NFO file cannot be parsed.
    
    This exception is raised when the parser cannot understand the format
    or structure of an NFO file, such as malformed XML or invalid JSON.
    
    Attributes:
        format_attempted (Optional[str]): The format that was attempted during parsing
        parse_details (Optional[str]): Additional parsing error information
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        format_attempted: Optional[str] = None,
        parse_details: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize parse error.
        
        Args:
            message: Human-readable error description
            file_path: Optional path to the file that caused the error
            format_attempted: The format that was attempted during parsing
            parse_details: Additional parsing error information
            **kwargs: Additional details passed to parent class
        """
        super().__init__(message, file_path, kwargs)
        self.format_attempted = format_attempted
        self.parse_details = parse_details


class NFOFieldError(NFOError):
    """
    Raised when field operations fail.
    
    This exception is raised when attempting to access, modify, or validate
    fields in an NFO file, such as when a field doesn't exist or has an
    invalid value.
    
    Attributes:
        field_name (Optional[str]): Name of the field that caused the error
        field_value (Optional[Any]): Value that caused the error (if applicable)
        operation (Optional[str]): The operation that failed (get, set, validate, etc.)
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        operation: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize field error.
        
        Args:
            message: Human-readable error description
            field_name: Name of the field that caused the error
            field_value: Value that caused the error (if applicable)
            operation: The operation that failed
            file_path: Optional path to the file that caused the error
            **kwargs: Additional details passed to parent class
        """
        super().__init__(message, file_path, kwargs)
        self.field_name = field_name
        self.field_value = field_value
        self.operation = operation


class NFOAccessError(NFOError):
    """
    Raised when file access operations fail.
    
    This exception is raised when the library cannot read from or write to
    NFO files due to permissions, file locks, missing files, or I/O errors.
    
    Attributes:
        access_mode (Optional[str]): The access mode that failed (read, write, etc.)
        system_error (Optional[str]): The underlying system error message
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        access_mode: Optional[str] = None,
        system_error: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize access error.
        
        Args:
            message: Human-readable error description
            file_path: Path to the file that caused the error
            access_mode: The access mode that failed
            system_error: The underlying system error message
            **kwargs: Additional details passed to parent class
        """
        super().__init__(message, file_path, kwargs)
        self.access_mode = access_mode
        self.system_error = system_error


class NFOFormatError(NFOError):
    """
    Raised when NFO file format is not supported or recognized.
    
    This exception is raised when the library cannot determine the format
    of an NFO file or when a requested format is not supported.
    
    Attributes:
        detected_format (Optional[str]): The format that was detected (if any)
        supported_formats (Optional[list]): List of supported formats
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        detected_format: Optional[str] = None,
        supported_formats: Optional[list] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize format error.
        
        Args:
            message: Human-readable error description
            file_path: Path to the file that caused the error
            detected_format: The format that was detected (if any)
            supported_formats: List of supported formats
            **kwargs: Additional details passed to parent class
        """
        super().__init__(message, file_path, kwargs)
        self.detected_format = detected_format
        self.supported_formats = supported_formats or []
