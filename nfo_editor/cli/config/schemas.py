"""
Configuration Schemas

Comprehensive Pydantic models for NFO Editor configuration validation.
Designed for extensibility and clear documentation to help users understand
exactly what each setting does and how it affects the application behavior.

Author: NFO Editor Team
"""

from typing import Dict, List, Optional, Union, Any, Literal
from pathlib import Path
from pydantic import BaseModel, Field, validator, root_validator
import os
from datetime import datetime


class DirectoryConfig(BaseModel):
    """
    Directory configuration for media libraries.
    
    This section defines directories where NFO files are located and
    how they should be processed.
    """
    
    movies: Optional[str] = Field(
        default=None,
        description="Path to movie NFO files directory. Can use ~ for home directory.",
        example="/media/movies"
    )
    
    tv: Optional[str] = Field(
        default=None, 
        description="Path to TV show NFO files directory. Can use ~ for home directory.",
        example="/media/tv-shows"
    )
    
    music: Optional[str] = Field(
        default=None,
        description="Path to music album NFO files directory. Can use ~ for home directory.", 
        example="/media/music"
    )
    
    custom_dirs: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Custom named directories for specialized collections.",
        example={"documentaries": "/media/docs", "anime": "/media/anime"}
    )
    
    @validator('movies', 'tv', 'music', pre=True)
    def expand_home_path(cls, v):
        """Expand ~ to home directory path."""
        if v and isinstance(v, str):
            return os.path.expanduser(v)
        return v
    
    @validator('custom_dirs', pre=True)
    def expand_custom_paths(cls, v):
        """Expand ~ in custom directory paths."""
        if v and isinstance(v, dict):
            return {k: os.path.expanduser(path) for k, path in v.items()}
        return v or {}


class RichDisplayConfig(BaseModel):
    """
    Rich terminal display configuration.
    
    Controls the appearance and behavior of terminal output including
    colors, themes, progress bars, and formatting options.
    """
    
    theme: Literal["auto", "dark", "light", "monokai"] = Field(
        default="auto",
        description=(
            "Color theme for terminal output. 'auto' detects terminal preferences, "
            "'dark'/'light' use appropriate color schemes, 'monokai' uses custom colors."
        )
    )
    
    show_progress: bool = Field(
        default=True,
        description=(
            "Display progress bars during batch operations. Set to False to disable "
            "progress tracking (useful for scripting or CI environments)."
        )
    )
    
    color_output: Literal["auto", "always", "never"] = Field(
        default="auto", 
        description=(
            "When to use colored output. 'auto' detects terminal capability, "
            "'always' forces colors, 'never' disables colors completely."
        )
    )
    
    table_style: str = Field(
        default="rounded",
        description=(
            "Style for table borders and formatting. Options: 'rounded', 'heavy', "
            "'double', 'simple', 'minimal'. Affects scan results and field displays."
        )
    )
    
    max_content_preview: int = Field(
        default=2000,
        ge=100,
        le=10000,
        description=(
            "Maximum characters to show in content preview. Larger files will be "
            "truncated to this length for display performance."
        )
    )
    
    syntax_highlighting: bool = Field(
        default=True,
        description=(
            "Enable syntax highlighting for NFO content display. XML, JSON, and "
            "other formats will be highlighted when viewing file contents."
        )
    )


class ScanConfig(BaseModel):
    """
    File scanning configuration.
    
    Controls how NFO files are discovered and filtered during scan operations.
    """
    
    pattern: str = Field(
        default="*.nfo",
        description=(
            "Glob pattern for matching NFO files. Default matches all .nfo files. "
            "Examples: '*movie*.nfo', '*.xml', '*episode*'"
        ),
        example="*.nfo"
    )
    
    recursive: bool = Field(
        default=True,
        description=(
            "Scan subdirectories recursively. When True, scans all nested folders. "
            "Set to False to scan only the specified directory."
        )
    )
    
    max_depth: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description=(
            "Maximum directory depth for recursive scanning. Prevents excessive "
            "nesting. None means unlimited depth (not recommended for large filesystems)."
        )
    )
    
    follow_symlinks: bool = Field(
        default=False,
        description=(
            "Follow symbolic links during directory scanning. Warning: Can cause "
            "infinite loops if symlinks create circular references."
        )
    )
    
    ignore_patterns: List[str] = Field(
        default_factory=lambda: [".*", "__pycache__", "*.tmp", "*.bak"],
        description=(
            "List of glob patterns to ignore during scanning. Files/directories "
            "matching these patterns will be skipped."
        )
    )


class EditConfig(BaseModel):
    """
    File editing configuration.
    
    Default settings for NFO file modification operations including backups,
    output formats, and batch operation limits.
    """
    
    backup: bool = Field(
        default=True,
        description=(
            "Create backup files before editing. Backups are saved with .backup "
            "extension. Highly recommended for data safety."
        )
    )
    
    backup_dir: Optional[str] = Field(
        default=None,
        description=(
            "Directory to store backup files. If None, backups are created in the "
            "same directory as the original file with .backup extension."
        )
    )
    
    output_format: Optional[Literal["xml", "json", "text"]] = Field(
        default=None,
        description=(
            "Default output format for edited files. If None, preserves the original "
            "format. 'xml' converts to XML, 'json' to JSON, 'text' to plain text."
        )
    )
    
    preserve_format: bool = Field(
        default=True,
        description=(
            "Preserve the original file format when editing. When True, ignores "
            "output_format setting and maintains the detected format."
        )
    )
    
    max_files: Optional[int] = Field(
        default=1000,
        ge=1,
        description=(
            "Maximum number of files to process in a single batch operation. "
            "Prevents accidental processing of huge directories. None means unlimited."
        )
    )
    
    dry_run_default: bool = Field(
        default=False,
        description=(
            "Enable dry-run mode by default. When True, shows what would be changed "
            "without actually modifying files. Good for testing configurations."
        )
    )


class FieldTemplateConfig(BaseModel):
    """
    Field template configuration.
    
    Defines reusable field templates with predefined values and transformations.
    Templates can include variables that are expanded at runtime.
    """
    
    name: str = Field(
        description="Unique name for this field template."
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of what this template does."
    )
    
    fields: Dict[str, Any] = Field(
        description=(
            "Dictionary of field names and values. Supports variables like {{now}}, "
            "{{date}}, {{filename}}, {{directory}} that are expanded during application."
        ),
        example={"updated": "{{now}}", "editor": "NFO Editor v2.0", "source": "manual"}
    )
    
    conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Optional conditions for when to apply this template. Can check existing "
            "field values or file properties before applying changes."
        )
    )


class ProfileConfig(BaseModel):
    """
    Profile configuration for reusable workflows.
    
    Profiles combine directory selections, field updates, and processing options
    into named configurations that can be easily reused for common tasks.
    """
    
    name: str = Field(
        description="Unique name for this profile."
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of what this profile does."
    )
    
    directories: List[str] = Field(
        description=(
            "List of directory names or paths to process. Can reference directory "
            "names from the directories section (e.g. ['movies', 'tv']) or use full paths."
        ),
        example=["movies", "tv"]
    )
    
    field_updates: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Dictionary of field names and values to update. Supports the same "
            "variable expansion as field templates."
        )
    )
    
    field_templates: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "List of field template names to apply. Templates are applied in order "
            "after direct field updates."
        )
    )
    
    scan_options: Optional[ScanConfig] = Field(
        default=None,
        description="Override scan settings for this profile."
    )
    
    edit_options: Optional[EditConfig] = Field(
        default=None, 
        description="Override edit settings for this profile."
    )
    
    patterns: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "List of file patterns to match. If empty, uses default pattern from "
            "scan configuration. Multiple patterns are OR'd together."
        ),
        example=["*movie*.nfo", "*film*.xml"]
    )


class LoggingConfig(BaseModel):
    """
    Logging configuration.
    
    Controls how the application logs operations and errors, useful for
    debugging and audit trails.
    """
    
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description=(
            "Minimum log level to record. DEBUG shows everything, INFO shows normal "
            "operations, WARNING shows potential issues, ERROR shows only failures."
        )
    )
    
    file: Optional[str] = Field(
        default=None,
        description=(
            "Path to log file. If None, logs only to console. File will be created "
            "if it doesn't exist. Use ~ for home directory."
        )
    )
    
    max_size_mb: int = Field(
        default=10,
        ge=1,
        le=1000,
        description=(
            "Maximum log file size in megabytes before rotation. When exceeded, "
            "old logs are archived and a new log file is started."
        )
    )
    
    backup_count: int = Field(
        default=3,
        ge=1,
        le=10,
        description=(
            "Number of backup log files to keep after rotation. Older backups "
            "are automatically deleted."
        )
    )


class NFOEditorConfig(BaseModel):
    """
    Main NFO Editor configuration.
    
    This is the root configuration model that contains all settings for the
    NFO Editor application. It provides sensible defaults while allowing
    comprehensive customization of behavior.
    
    Configuration files should be YAML format and can be placed in:
    - Current directory: nfo-editor.yaml
    - Home directory: ~/.nfo-editor.yaml  
    - XDG config directory: ~/.config/nfo-editor/config.yaml
    """
    
    # Metadata
    version: str = Field(
        default="2.0",
        description="Configuration file version for compatibility checking."
    )
    
    default_mode: Literal["interactive", "cli"] = Field(
        default="interactive",
        description=(
            "Default operating mode when no arguments are provided. 'interactive' "
            "launches the TUI interface, 'cli' shows help message."
        )
    )
    
    # Core configuration sections
    directories: DirectoryConfig = Field(
        default_factory=DirectoryConfig,
        description="Directory paths where NFO files are located."
    )
    
    rich: RichDisplayConfig = Field(
        default_factory=RichDisplayConfig,
        description="Terminal display and formatting options."
    )
    
    scan: ScanConfig = Field(
        default_factory=ScanConfig,
        description="File scanning behavior and filtering options."
    )
    
    edit: EditConfig = Field(
        default_factory=EditConfig,
        description="Default settings for file editing operations."
    )
    
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration for debugging and audit trails."
    )
    
    # Advanced features
    field_templates: List[FieldTemplateConfig] = Field(
        default_factory=list,
        description="Reusable field templates for common update patterns."
    )
    
    profiles: List[ProfileConfig] = Field(
        default_factory=list,
        description="Named profiles that combine settings for specific workflows."
    )
    
    # Environment variable overrides
    env_prefix: str = Field(
        default="NFO_EDITOR_",
        description=(
            "Prefix for environment variables that override configuration values. "
            "Example: NFO_EDITOR_DEFAULT_MODE=cli"
        )
    )
    
    # Extension points for future features
    plugins: Dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin configuration (reserved for future use)."
    )
    
    custom: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom user-defined configuration values."
    )
    
    class Config:
        extra = "forbid"  # Prevents typos in config files
        validate_assignment = True  # Validates when values are changed
        use_enum_values = True  # Use enum values in output
        json_encoders = {
            Path: str,
            datetime: lambda dt: dt.isoformat()
        }


# Export the main classes for easy importing
__all__ = [
    "NFOEditorConfig",
    "ProfileConfig", 
    "RichDisplayConfig",
    "DirectoryConfig",
    "ScanConfig",
    "EditConfig",
    "FieldTemplateConfig",
    "LoggingConfig"
]
