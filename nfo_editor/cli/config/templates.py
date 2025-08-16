"""
Configuration Templates

Generates comprehensive, well-documented YAML configuration templates
that help users understand exactly what each setting does and how it
affects the application behavior.

Author: NFO Editor Team
"""

from datetime import datetime


def generate_config_template(include_examples: bool = True, 
                           include_comments: bool = True) -> str:
    """
    Generate a comprehensive YAML configuration template.
    
    Args:
        include_examples: Whether to include example values
        include_comments: Whether to include detailed comments
        
    Returns:
        YAML configuration template as string with full documentation
    """
    template = []
    
    if include_comments:
        template.extend([
            "# NFO Editor Configuration File",
            "# ================================",
            "#",
            "# This file controls all aspects of NFO Editor behavior.",
            "# Place this file in one of these locations:",
            "#   - Current directory: nfo-editor.yaml",
            "#   - Home directory: ~/.nfo-editor.yaml",
            "#   - XDG config: ~/.config/nfo-editor/config.yaml",
            "#",
            f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# For full documentation: https://github.com/your-repo/nfo-editor",
            "",
            "# Configuration file version (for compatibility checking)",
            "version: \"2.0\"",
            "",
            "# Default operating mode when no arguments are provided",
            "# Options: 'interactive' (TUI interface) or 'cli' (show help)",
            "default_mode: interactive",
            "",
        ])
    
    # Directories section
    if include_comments:
        template.extend([
            "# Directory Configuration",
            "# ======================",
            "# Define where your NFO files are located. Use ~ for home directory.",
            "# These directory names can be referenced in profiles.",
            "",
        ])
    
    template.extend([
        "directories:",
        "  # Path to movie NFO files",
        f"  movies: {'/media/movies' if include_examples else 'null'}",
        "  # Path to TV show NFO files", 
        f"  tv: {'/media/tv-shows' if include_examples else 'null'}",
        "  # Path to music album NFO files",
        f"  music: {'/media/music' if include_examples else 'null'}",
        "  # Custom named directories for specialized collections",
        "  custom_dirs:" + ("" if not include_examples else ""),
    ])
    
    if include_examples:
        template.extend([
            "    documentaries: /media/documentaries",
            "    anime: /media/anime",
            "    concerts: /media/concerts",
        ])
    
    template.append("")
    
    # Rich display configuration
    if include_comments:
        template.extend([
            "# Rich Terminal Display Configuration", 
            "# ===================================",
            "# Controls the appearance and behavior of terminal output",
            "",
        ])
    
    template.extend([
        "rich:",
        "  # Color theme: 'auto', 'dark', 'light', 'monokai'",
        "  # 'auto' detects terminal preferences automatically",
        "  theme: auto",
        "",
        "  # Show progress bars during batch operations",
        "  # Set to false for scripting or CI environments",
        "  show_progress: true",
        "",
        "  # When to use colored output: 'auto', 'always', 'never'",
        "  color_output: auto",
        "",
        "  # Table border style: 'rounded', 'heavy', 'double', 'simple', 'minimal'",
        "  table_style: rounded",
        "",
        "  # Maximum characters to show in content preview (100-10000)",
        "  max_content_preview: 2000",
        "",
        "  # Enable syntax highlighting for NFO content display",
        "  syntax_highlighting: true",
        "",
    ])
    
    # Scanning configuration  
    template.extend([
        "scan:",
        "  # Glob pattern for matching NFO files",
        "  pattern: \"*.nfo\"",
        "  # Scan subdirectories recursively", 
        "  recursive: true",
        "  # Maximum directory depth (null = unlimited)",
        "  max_depth: null",
        "  # Follow symbolic links",
        "  follow_symlinks: false",
        "  # Patterns to ignore during scanning",
        "  ignore_patterns:",
        "    - \".*\"",
        "    - \"__pycache__\"", 
        "    - \"*.tmp\"",
        "    - \"*.bak\"",
        "",
    ])
    
    # Edit configuration
    template.extend([
        "edit:",
        "  # Create backup files before editing",
        "  backup: true",
        "  # Directory for backups (null = same as original)", 
        "  backup_dir: null",
        "  # Default output format (null = preserve original)",
        "  output_format: null",
        "  # Preserve original format when editing",
        "  preserve_format: true",
        "  # Maximum files to process in single batch",
        "  max_files: 1000", 
        "  # Enable dry-run mode by default",
        "  dry_run_default: false",
        "",
    ])
    
    # Profiles section
    template.extend([
        "profiles:",
    ])
    
    if include_examples:
        template.extend([
            "  # Movie cleanup profile",
            "  - name: movie_cleanup", 
            "    description: \"Clean and standardize movie NFO files\"",
            "    directories: [\"movies\"]",
            "    field_updates:",
            "      updated: \"{{now}}\"",
            "      studio: \"Various\"",
            "    patterns: [\"*movie*.nfo\"]",
            "",
            "  # TV show profile",
            "  - name: tv_standardize",
            "    description: \"Standardize TV show information\"", 
            "    directories: [\"tv\"]",
            "    field_updates:",
            "      format: \"TV Series\"",
            "      updated: \"{{now}}\"",
            "",
        ])
    
    template.extend([
        "# Environment variable prefix",
        "env_prefix: \"NFO_EDITOR_\"",
        "",
        "# Plugin configuration (reserved)",
        "plugins: {}",
        "",
        "# Custom configuration values", 
        "custom: {}",
    ])
    
    return "\n".join(template)


def generate_minimal_config() -> str:
    """Generate minimal configuration template."""
    return """# Minimal NFO Editor Configuration
version: "2.0"

directories:
  movies: /media/movies
  tv: /media/tv-shows

rich:
  theme: auto
  show_progress: true

edit:
  backup: true
  preserve_format: true
"""
