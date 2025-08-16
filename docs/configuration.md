# 📋 Configuration Guide

Comprehensive guide to NFO Editor's YAML configuration system - from basic setup to advanced enterprise workflows.

## 🎯 Overview

NFO Editor v2.0 features a powerful configuration system that allows you to:
- **Define directory shortcuts** for your media collections
- **Create reusable profiles** for common workflows
- **Customize display and behavior** with rich options
- **Override settings** via environment variables
- **Validate configurations** with detailed error reporting

## 📍 Configuration File Locations

NFO Editor searches for configuration files in this order:

1. **Current directory**: `./nfo-editor.yaml`
2. **Current directory (hidden)**: `./.nfo-editor.yaml`
3. **Home directory**: `~/.nfo-editor.yaml`
4. **XDG config directory**: `~/.config/nfo-editor/config.yaml`
5. **Custom path**: `--config /path/to/config.yaml`

```bash
# See all search locations
nfo-editor --show-config-locations
```

## 🚀 Quick Start

### Generate Template
```bash
# Create a comprehensive configuration template
nfo-editor --generate-config > ~/.nfo-editor.yaml

# Or generate minimal template
nfo-editor --generate-config | grep -v '^#' > ~/.nfo-editor.yaml
```

### Basic Configuration
```yaml
# ~/.nfo-editor.yaml
version: "2.0"
default_mode: interactive

# Your media directories
directories:
  movies: /media/movies
  tv: /media/tv-shows
  music: /media/music

# Display preferences
rich:
  theme: auto
  show_progress: true
  syntax_highlighting: true
```

### Validate Configuration
```bash
# Validate your configuration
nfo-editor --validate-config

# Validate specific file
nfo-editor --config ~/.nfo-editor.yaml --validate-config
```

## 📋 Configuration Schema

### Root Level Settings

#### Version and Mode
```yaml
# Configuration version (required for compatibility)
version: "2.0"

# Default mode when launched without arguments
default_mode: interactive  # or 'cli'
```

#### Environment Variable Prefix
```yaml
# Prefix for environment variable overrides
env_prefix: "NFO_EDITOR_"  # Default

# Allows: NFO_EDITOR_RICH_THEME=dark nfo-editor
```

### Directory Configuration

Define shortcuts for your media collections:

```yaml
directories:
  # Standard media types
  movies: /media/movies
  tv: /media/tv-shows
  music: /media/music
  
  # Custom collections
  custom_dirs:
    documentaries: /media/documentaries
    anime: /media/anime
    concerts: /media/concerts
    home_videos: ~/Videos/personal
```

**Features:**
- **Tilde expansion**: `~/Videos` becomes `/home/user/Videos`
- **Profile references**: Use `movies` instead of `/media/movies` in profiles
- **Validation**: Ensures referenced directories are defined

### Rich Display Configuration

Control terminal appearance and behavior:

```yaml
rich:
  # Color theme selection
  theme: auto  # auto, dark, light, monokai
  
  # Progress bars during operations
  show_progress: true
  
  # Color output control
  color_output: auto  # auto, always, never
  
  # Table styling
  table_style: rounded  # rounded, heavy, double, simple, minimal
  
  # Content preview limits
  max_content_preview: 2000  # characters (100-10000)
  
  # Syntax highlighting
  syntax_highlighting: true
```

**Theme Options:**
- `auto` - Detects terminal preferences
- `dark` - Optimized for dark terminals  
- `light` - Optimized for light terminals
- `monokai` - Custom color scheme

### Scanning Configuration

Default behavior for file discovery:

```yaml
scan:
  # File matching pattern
  pattern: "*.nfo"  # or "*.xml", "*movie*.nfo"
  
  # Directory traversal
  recursive: true
  max_depth: null  # null = unlimited, or 1-20
  follow_symlinks: false
  
  # Files/directories to ignore
  ignore_patterns:
    - ".*"           # Hidden files
    - "__pycache__"  # Python cache
    - "*.tmp"        # Temporary files
    - "*.bak"        # Backup files
    - "Thumbs.db"    # Windows thumbnails
```

### Editing Configuration

Default behavior for file modifications:

```yaml
edit:
  # Backup configuration
  backup: true
  backup_dir: null  # null = same directory as original
  
  # Output format handling
  output_format: null      # null, xml, json, text
  preserve_format: true    # Override output_format
  
  # Safety limits
  max_files: 1000         # Maximum files per operation
  dry_run_default: false  # Default to actual changes
```

### Logging Configuration

Control operation logging and debugging:

```yaml
logging:
  # Log level
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  
  # Log file (null = console only)
  file: null  # or "/var/log/nfo-editor.log"
  
  # Log rotation
  max_size_mb: 10
  backup_count: 3
```

## 🔧 Profile System

Profiles combine settings for reusable workflows:

### Basic Profile Structure
```yaml
profiles:
  - name: movie_cleanup
    description: "Clean and standardize movie NFO files"
    
    # Which directories to process
    directories: [movies]  # References directories.movies
    
    # Field updates to apply
    field_updates:
      updated: "{{now}}"     # Variable expansion
      studio: "Various"
      source: "BluRay"
    
    # File matching patterns  
    patterns: ["*movie*.nfo", "*film*.xml"]
    
    # Override scan settings
    scan_options:
      recursive: true
      max_depth: 3
    
    # Override edit settings
    edit_options:
      backup: true
      max_files: 500
```

### Advanced Profile Example
```yaml
profiles:
  - name: tv_episode_processor
    description: "Comprehensive TV episode processing"
    
    directories: [tv, documentaries]
    
    # Complex field updates
    field_updates:
      format: "TV-{{resolution}}"
      updated: "{{date}}"
      processed_by: "NFO Editor v2.0"
      # Clear unwanted fields
      imdbid: null
      tmdbid: null
    
    # Apply field templates
    field_templates: [metadata_cleanup, quality_tags]
    
    patterns: 
      - "*episode*.nfo"
      - "*[Ss][0-9][0-9][Ee][0-9][0-9]*.xml"
    
    # Specialized scan settings
    scan_options:
      pattern: "*episode*.nfo"
      recursive: true
      max_depth: 2
      ignore_patterns: ["*sample*", "*trailer*"]
    
    # Conservative edit settings
    edit_options:
      backup: true
      backup_dir: "/backups/nfo"
      preserve_format: true
      max_files: 200
      dry_run_default: false
```

### Field Templates
Reusable field update templates:

```yaml
field_templates:
  - name: metadata_cleanup
    description: "Standard metadata cleanup"
    fields:
      updated: "{{now}}"
      editor: "NFO Editor v2.0"
      source: "manual"
  
  - name: quality_tags
    description: "Video quality standardization"
    fields:
      source: "BluRay"
      codec: "H.264"
      resolution: "1080p"
      
  - name: remove_ids
    description: "Remove external IDs"
    fields:
      imdbid: null
      tmdbid: null
      tvdbid: null
```

**Variable Expansion:**
- `{{now}}` - Current timestamp (ISO format)
- `{{date}}` - Current date (YYYY-MM-DD)
- `{{filename}}` - Current filename
- `{{directory}}` - Current directory name

## 🌍 Environment Variable Overrides

Override any configuration value using environment variables:

### Naming Convention
```bash
NFO_EDITOR_<SECTION>_<SETTING>=<VALUE>
```

### Common Overrides
```bash
# Theme and display
export NFO_EDITOR_RICH_THEME=monokai
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_RICH_COLOR_OUTPUT=always

# Default behavior  
export NFO_EDITOR_DEFAULT_MODE=cli

# Editing behavior
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_MAX_FILES=100
export NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=true

# Scanning behavior
export NFO_EDITOR_SCAN_PATTERN="*.xml"
export NFO_EDITOR_SCAN_RECURSIVE=false
```

### Nested Configuration
```bash
# For nested settings, use underscores
# rich.theme becomes RICH_THEME
# scan.max_depth becomes SCAN_MAX_DEPTH
# edit.backup_dir becomes EDIT_BACKUP_DIR
```

### Type Conversion
Environment variables are automatically converted:
- **Booleans**: `true/false`, `1/0`, `yes/no`, `on/off`
- **Numbers**: `123`, `45.67`
- **Strings**: Everything else

## 🔍 Validation and Error Handling

### Validation Commands
```bash
# Validate auto-discovered configuration
nfo-editor --validate-config

# Validate specific file
nfo-editor --config /path/to/config.yaml --validate-config

# Test with environment overrides
NFO_EDITOR_RICH_THEME=invalid nfo-editor --validate-config
```

### Common Validation Errors

#### 1. Invalid Profile References
```yaml
# ERROR: Profile references unknown directory
profiles:
  - name: test
    directories: [nonexistent]  # 'nonexistent' not in directories
```

**Solution:**
```yaml
directories:
  nonexistent: /path/to/directory

profiles:
  - name: test
    directories: [nonexistent]  # Now valid
```

#### 2. Invalid Field Template References
```yaml
# ERROR: Profile references unknown template
profiles:
  - name: test
    field_templates: [missing_template]
```

**Solution:**
```yaml
field_templates:
  - name: missing_template
    fields:
      test: value

profiles:
  - name: test
    field_templates: [missing_template]  # Now valid
```

#### 3. Type Validation Errors
```yaml
# ERROR: Invalid types
rich:
  theme: invalid_theme      # Must be auto, dark, light, monokai
  max_content_preview: -1   # Must be 100-10000
  
scan:
  max_depth: 50            # Must be 1-20 or null
```

## 📁 Configuration Examples

### Media Server Configuration
```yaml
version: "2.0"
default_mode: cli  # Headless server environment

directories:
  movies: /mnt/storage/movies
  tv: /mnt/storage/tv
  music: /mnt/storage/music
  incoming: /mnt/incoming

rich:
  theme: auto
  show_progress: false  # Disable for cron jobs
  color_output: never   # Plain output for logs

profiles:
  - name: process_incoming
    description: "Process new media files"
    directories: [incoming]
    field_updates:
      processed_date: "{{now}}"
      source: "automated"
    edit_options:
      backup: true
      backup_dir: "/mnt/backups/nfo"
      max_files: 50

  - name: monthly_cleanup  
    description: "Monthly metadata cleanup"
    directories: [movies, tv]
    field_templates: [metadata_cleanup]
    edit_options:
      backup: true
      max_files: 1000

field_templates:
  - name: metadata_cleanup
    fields:
      last_updated: "{{now}}"
      cleaned_by: "automated_process"
```

### Development Configuration
```yaml
version: "2.0"
default_mode: interactive

directories:
  test_data: ./test-media
  examples: ./examples
  fixtures: ./tests/fixtures

rich:
  theme: monokai
  show_progress: true
  syntax_highlighting: true

logging:
  level: DEBUG
  file: "./nfo-editor-debug.log"

profiles:
  - name: test_run
    description: "Test profile for development"
    directories: [test_data]
    field_updates:
      test_run: "{{now}}"
    edit_options:
      backup: true
      dry_run_default: true
      max_files: 5
```

### Enterprise Configuration
```yaml
version: "2.0"
default_mode: interactive

directories:
  movies: /media/library/movies
  tv_shows: /media/library/tv
  documentaries: /media/library/docs
  custom_dirs:
    archived: /media/archive
    processing: /media/processing
    quarantine: /media/quarantine

rich:
  theme: auto
  show_progress: true
  color_output: auto
  table_style: rounded

scan:
  recursive: true
  max_depth: 5
  follow_symlinks: false
  ignore_patterns:
    - ".*"
    - "@eaDir"  # Synology
    - "#recycle"
    - "*.partial"

edit:
  backup: true
  backup_dir: /media/backups/nfo
  preserve_format: true
  max_files: 500

logging:
  level: INFO
  file: /var/log/nfo-editor.log
  max_size_mb: 50
  backup_count: 5

field_templates:
  - name: studio_standard
    description: "Studio standardization"
    fields:
      updated: "{{now}}"
      processed_by: "Media Team"
      quality_check: true

  - name: archive_metadata
    description: "Archival metadata"
    fields:
      archived_date: "{{date}}"
      archive_version: "v2.0"
      retention_policy: "7_years"

profiles:
  - name: new_acquisitions
    description: "Process newly acquired content"
    directories: [processing]
    field_templates: [studio_standard]
    scan_options:
      pattern: "*.nfo"
      recursive: true
    edit_options:
      backup: true
      max_files: 100

  - name: quality_assurance
    description: "QA workflow for media files"
    directories: [movies, tv_shows]
    field_updates:
      qa_date: "{{now}}"
      qa_passed: true
    edit_options:
      backup: true
      preserve_format: true

  - name: archive_preparation
    description: "Prepare content for archival"
    directories: [archived]
    field_templates: [archive_metadata]
    edit_options:
      backup: true
      backup_dir: /media/backups/archive
```

## 🔧 Configuration Management Tips

### 1. Start Simple
Begin with basic directory mappings and gradually add profiles.

### 2. Use Validation
Always validate configuration changes:
```bash
nfo-editor --validate-config
```

### 3. Test with Dry-Run
Test profiles before applying:
```bash
nfo-editor --profile my_profile --edit /media --dry-run
```

### 4. Environment Overrides for Testing
```bash
# Test with different settings temporarily
NFO_EDITOR_EDIT_MAX_FILES=5 nfo-editor --profile test_profile
```

### 5. Version Control
Keep configuration files in version control for team sharing.

### 6. Documentation
Document your profiles and field templates clearly:
```yaml
profiles:
  - name: movie_standardization
    description: |
      Standardizes movie NFO files by:
      - Adding processing timestamp
      - Normalizing studio names
      - Setting consistent quality tags
      Used by: Media team for new acquisitions
```

## 🔗 Next Steps

- **[🔧 Profile Management](profiles.md)** - Deep dive into profile workflows
- **[🌍 Environment Variables](environment.md)** - Comprehensive environment integration
- **[⚡ CLI Commands](cli-commands.md)** - Using configuration with CLI commands

---

For configuration troubleshooting, see the validation commands and error handling sections above, or refer to the **[Development Guide](development.md)** for debugging techniques.
