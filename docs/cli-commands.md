# ⚡ CLI Commands Reference

Complete reference for NFO Editor v2.0 command-line interface with examples and detailed explanations.

## 📋 Command Overview

NFO Editor uses a **flag-based CLI design** where all operations are accessed through global options rather than subcommands. This provides a consistent interface while maintaining powerful functionality.

### Basic Syntax
```bash
nfo-editor [GLOBAL_OPTIONS] [COMMAND_FLAGS] [ARGUMENTS]
```

## 🎮 Core Usage Modes

### Default Interactive Mode
```bash
# Launch interactive TUI (default when no flags provided)
nfo-editor

# Launch with specific configuration
nfo-editor --config ~/workflows.yaml

# Launch with environment overrides
NFO_EDITOR_RICH_THEME=monokai nfo-editor
```

## 📁 File Discovery Commands

### `--scan` - Directory Scanning
Scan directories for NFO files with professional output.

```bash
# Basic directory scan
nfo-editor --scan /media/movies

# Multiple directories
nfo-editor --scan /media/movies /media/tv /media/music

# With pattern filtering
nfo-editor --scan /media/movies --pattern "*movie*.nfo"

# Non-recursive scan
nfo-editor --scan /media/movies --no-recursive

# Different output formats
nfo-editor --scan /media --format table    # Default: professional table
nfo-editor --scan /media --format json     # JSON output
nfo-editor --scan /media --format list     # Simple file list
nfo-editor --scan /media --format yaml     # YAML output
```

**Examples:**
```bash
# Scan movies directory with custom pattern
nfo-editor --scan /media/movies --pattern "*.xml" --format table

# Quick JSON export of all NFO files
nfo-editor --scan /media --format json > nfo-inventory.json

# Scan with progress tracking (multiple directories)
nfo-editor --scan /media/movies /media/tv --format table
```

### `--detect` - Format Detection  
Detect and analyze NFO file format with confidence scoring.

```bash
# Detect single file format
nfo-editor --detect /media/movie.nfo

# With custom theme
nfo-editor --detect /media/movie.nfo --theme monokai

# JSON output for scripting
nfo-editor --detect /media/movie.nfo --format json
```

**Output Example:**
```
╭────────── 🔍 Format Detection ──────────╮
│ File: /media/movie.nfo                 │
│ Format: XML                            │
│ Confidence: 🟢 98.5%                   │
│ Encoding: UTF-8                        │
│ Fallback Formats: JSON, TEXT           │
╰────────────────────────────────────────╯
```

## 📖 Content Display Commands

### `--load` - File Content Display
Load and display NFO file contents with syntax highlighting.

```bash
# Load and display full file
nfo-editor --load /media/movie.nfo

# Show specific fields only
nfo-editor --load /media/movie.nfo --fields title,year,genre

# Multiple fields with different output
nfo-editor --load /media/movie.nfo --fields title,plot,cast --format table
nfo-editor --load /media/movie.nfo --format json
```

**Features:**
- Syntax highlighting for XML, JSON, text
- Professional table display with metadata
- Field filtering and selection
- Multiple output formats

**Examples:**
```bash
# Quick movie info
nfo-editor --load /media/movie.nfo --fields title,year,rating

# Export to JSON for processing
nfo-editor --load /media/episode.nfo --format json > episode-data.json

# Preview with custom theme
nfo-editor --load /media/movie.xml --theme monokai
```

## ✏️ File Editing Commands

### `--edit` - Batch File Editing
Edit NFO files with field updates, backups, and safety features.

```bash
# Basic field updates
nfo-editor --edit /media/movies --set genre=Action year=2024

# Multiple field updates
nfo-editor --edit /media/tv --set genre=Drama studio="HBO" updated="2024-01-15"

# With pattern filtering
nfo-editor --edit /media --set studio=Universal --pattern "*movie*.nfo"

# Safety features
nfo-editor --edit /media/movies --set year=2024 --dry-run      # Preview only
nfo-editor --edit /media/movies --set year=2024 --backup       # Create backups
nfo-editor --edit /media/movies --set year=2024 --no-backup    # Skip backups

# Batch limits
nfo-editor --edit /media/movies --set year=2024 --max-files 10

# Output format conversion
nfo-editor --edit /media/movies --output-format json --backup
```

**Field Update Format:**
- `field=value` - Set simple field
- `nested.field=value` - Set nested field  
- `field=` - Clear field (set to empty)

**Examples:**
```bash
# Update movie ratings
nfo-editor --edit /media/movies --set rating=8.5 --pattern "*movie*.nfo" --dry-run

# Standardize TV shows
nfo-editor --edit /media/tv --set format="TV Series" source="Streaming" --backup

# Convert format with backup
nfo-editor --edit /media/old-nfos --output-format xml --backup

# Limited batch processing
nfo-editor --edit /media/huge-collection --set updated="2024-01-15" --max-files 100
```

## ⚙️ Configuration Commands

### `--generate-config` - Configuration Template
Generate comprehensive configuration templates.

```bash
# Generate full configuration template
nfo-editor --generate-config

# Save to file
nfo-editor --generate-config > ~/.nfo-editor.yaml

# Pipe to editor
nfo-editor --generate-config | code -
```

### `--validate-config` - Configuration Validation
Validate configuration files with detailed error reporting.

```bash
# Validate auto-discovered config
nfo-editor --validate-config

# Validate specific file
nfo-editor --config /path/to/config.yaml --validate-config

# With environment overrides
NFO_EDITOR_RICH_THEME=invalid nfo-editor --validate-config
```

### `--show-config-locations` - Config Discovery
Show configuration file search locations.

```bash
nfo-editor --show-config-locations
```

**Output:**
```
╭────────── 📁 Config Discovery ──────────╮
│ Configuration file locations:           │
│   1. ./nfo-editor.yaml                 │
│   2. ./.nfo-editor.yaml                │  
│   3. ~/.nfo-editor.yaml                │
│   4. ~/.config/nfo-editor/config.yaml  │
╰─────────────────────────────────────────╯
```

### `--list-profiles` - Profile Management
List available configuration profiles.

```bash
# List all profiles
nfo-editor --list-profiles

# From specific config
nfo-editor --config workflows.yaml --list-profiles
```

## 📋 Profile System

### `--profile` - Profile Execution
Use predefined configuration profiles for complex workflows.

```bash
# Use profile for scanning
nfo-editor --profile movie_cleanup --scan

# Use profile for editing  
nfo-editor --profile tv_standardize --edit /media/tv

# Override profile settings
nfo-editor --profile movie_cleanup --max-files 50 --dry-run

# Profile with custom directories
nfo-editor --profile tv_episodes --edit /media/custom-tv
```

**Profile Benefits:**
- Predefined field updates
- Directory shortcuts
- Custom patterns and limits
- Reusable workflows
- Team sharing capability

## 🎨 Display & Theming Options

### `--theme` - Theme Selection
Control terminal color themes and styling.

```bash
# Available themes
nfo-editor --scan /media --theme auto      # Auto-detect (default)
nfo-editor --scan /media --theme dark      # Dark theme
nfo-editor --scan /media --theme light     # Light theme  
nfo-editor --scan /media --theme monokai   # Monokai colors

# Apply globally via environment
NFO_EDITOR_RICH_THEME=monokai nfo-editor --scan /media
```

### `--format` - Output Format Control
Control output format for scan, detect, and load commands.

```bash
# Table format (default) - Professional tables with metadata
nfo-editor --scan /media --format table

# JSON format - Structured data for scripts
nfo-editor --scan /media --format json

# List format - Simple file paths
nfo-editor --scan /media --format list  

# YAML format - Human-readable structured data
nfo-editor --load movie.nfo --format yaml
```

## 🔧 Global Options

### Configuration Options
```bash
-c, --config PATH          # Path to YAML configuration file
--profile TEXT             # Use specific configuration profile
```

### Output Control
```bash
-v, --verbose              # Enable verbose output
-q, --quiet               # Suppress non-error output (useful for scripts)
--theme [auto|dark|light|monokai]  # Color theme
```

### Help & Information
```bash
--help                    # Show help message
--version                 # Show version information
```

## 🌍 Environment Variable Integration

Override any configuration setting using environment variables:

### Common Overrides
```bash
# Theme and display
export NFO_EDITOR_RICH_THEME=monokai
export NFO_EDITOR_RICH_SHOW_PROGRESS=false

# Default behavior
export NFO_EDITOR_DEFAULT_MODE=cli

# Editing defaults
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_MAX_FILES=500

# Use with commands
NFO_EDITOR_RICH_THEME=dark nfo-editor --scan /media
```

### Environment Variable Format
- Prefix: `NFO_EDITOR_`
- Nested paths: `NFO_EDITOR_RICH_THEME` sets `rich.theme`
- Boolean values: `true/false`, `1/0`, `yes/no`
- Numeric values: Automatically converted

## 📊 Output Format Examples

### Table Format (Default)
```
                📂 Scan Summary                
┌─────────────────────┬─────────────────────┐
│ NFO files found     │ 1,247               │
│ Directories scanned │ 15                  │
│ Total files scanned │ 45,892              │
│ Scan time           │ 2.34s               │
└─────────────────────┴─────────────────────┘
```

### JSON Format
```json
{
  "nfo_files": [
    "/media/movie1.nfo",
    "/media/movie2.xml"
  ],
  "directories_scanned": 2,
  "total_files_scanned": 1247,
  "scan_time_seconds": 2.34,
  "errors": []
}
```

### List Format
```
/media/movies/inception.nfo
/media/movies/matrix.xml
/media/tv/episode1.nfo
```

## 🔧 Advanced Usage Patterns

### Scripting Integration
```bash
#!/bin/bash
# Automated NFO processing script

# Set environment for batch processing
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_EDIT_BACKUP=true

# Process different collections
nfo-editor --edit /media/movies --set updated="$(date)" --max-files 100
nfo-editor --edit /media/tv --set format="TV Series" --profile tv_standardize

# Generate reports
nfo-editor --scan /media --format json > daily-nfo-report.json
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Validate NFO files
  run: |
    export NFO_EDITOR_DEFAULT_MODE=cli
    nfo-editor --scan ./media --format json > nfo-report.json
    nfo-editor --validate-config
```

### Complex Workflows
```bash
# Multi-step processing with profiles
nfo-editor --profile initial_scan --scan /media/new-content
nfo-editor --profile cleanup_metadata --edit /media/new-content --dry-run
nfo-editor --profile finalize_content --edit /media/new-content --backup
```

## 🆘 Troubleshooting Commands

### Validation and Debugging
```bash
# Validate configuration
nfo-editor --validate-config

# Check available profiles
nfo-editor --list-profiles

# Test configuration with dry-run
nfo-editor --profile my_profile --edit /media --dry-run

# Verbose output for debugging
nfo-editor --verbose --scan /media --format table
```

### Common Error Solutions
```bash
# Permission issues - use dry-run first
nfo-editor --edit /media --set test=value --dry-run

# Large directories - use limits
nfo-editor --scan /huge/media --max-files 1000

# Configuration errors - validate first
nfo-editor --config my-config.yaml --validate-config
```

---

For more detailed information, see:
- **[📋 Configuration Guide](configuration.md)** - YAML configuration system
- **[🔧 Profile Management](profiles.md)** - Creating and using profiles
- **[🎨 Themes & Formatting](themes.md)** - Customizing visual output
