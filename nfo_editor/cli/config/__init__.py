"""
Configuration Management Package

Handles YAML configuration file loading, validation, and profile management.
Supports config discovery and Pydantic-based validation schemas.

Author: NFO Editor Team
"""

from .loader import ConfigLoader
from .schemas import NFOEditorConfig, ProfileConfig, RichDisplayConfig
from .templates import generate_config_template

__all__ = [
    "ConfigLoader",
    "NFOEditorConfig", 
    "ProfileConfig",
    "RichDisplayConfig",
    "generate_config_template"
]
