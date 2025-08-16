# 🔧 Profile Management

Master NFO Editor's profile system to create powerful, reusable workflows for common tasks and complex media processing scenarios.

## 🎯 What Are Profiles?

Profiles are **named configuration bundles** that combine:
- **Directory selections** (which folders to process)
- **Field updates** (what changes to make)
- **Processing options** (scan and edit settings)  
- **File patterns** (which files to include)

Think of profiles as "recipes" for common NFO processing tasks.

## 🚀 Quick Start with Profiles

### List Available Profiles
```bash
# See profiles in your configuration
nfo-editor --list-profiles

# From specific config file
nfo-editor --config workflows.yaml --list-profiles
```

### Use a Profile
```bash
# Run profile with default action (interactive mode)
nfo-editor --profile movie_cleanup

# Use profile with specific command
nfo-editor --profile tv_episodes --scan
nfo-editor --profile movie_cleanup --edit /media/movies --dry-run

# Override profile settings
nfo-editor --profile bulk_update --max-files 50
```

## 📋 Profile Structure

### Basic Profile
```yaml
profiles:
  - name: movie_cleanup
    description: "Clean and standardize movie NFO files"
    
    # What directories to process
    directories: [movies]  # References directories.movies
    
    # What changes to make
    field_updates:
      updated: "{{now}}"
      studio: "Universal"
      source: "BluRay"
```

### Advanced Profile  
```yaml
profiles:
  - name: tv_episode_processor
    description: "Comprehensive TV episode processing workflow"
    
    # Multiple directory references
    directories: [tv, documentaries]
    
    # Complex field updates with variables
    field_updates:
      format: "TV-{{resolution}}"
      updated: "{{now}}"
      processed_by: "Automation"
      # Clear unwanted fields
      old_field: null
    
    # Apply reusable field templates
    field_templates: [metadata_cleanup, quality_tags]
    
    # Custom file patterns
    patterns: 
      - "*episode*.nfo"
      - "*[Ss][0-9][0-9][Ee][0-9][0-9]*.xml"
    
    # Override scan settings
    scan_options:
      recursive: true
      max_depth: 2
      ignore_patterns: ["*sample*", "*trailer*"]
    
    # Override edit settings
    edit_options:
      backup: true
      backup_dir: "/backups/tv"
      max_files: 100
```

## 🏗️ Profile Components

### 1. Directory Selection
Reference configured directories by name:

```yaml
# In your configuration
directories:
  movies: /media/movies
  tv: /media/tv-shows
  documentaries: /media/docs

profiles:
  - name: all_media
    directories: [movies, tv, documentaries]  # Use all three
    
  - name: movies_only  
    directories: [movies]  # Just movies
    
  - name: mixed_content
    directories: [tv, documentaries]  # Subset
```

**Benefits:**
- **Readable**: Use `movies` instead of `/media/movies`
- **Maintainable**: Change path once, affects all profiles
- **Portable**: Share profiles without hardcoded paths

### 2. Field Updates
Define what changes to make to NFO files:

```yaml
profiles:
  - name: field_examples
    directories: [movies]
    field_updates:
      # Simple field updates
      studio: "Universal Pictures"
      rating: 8.5
      updated: "{{now}}"
      
      # Nested field updates  
      metadata.source: "BluRay"
      cast.director: "Christopher Nolan"
      
      # Clear fields (set to null/empty)
      imdbid: null
      unwanted_field: ""
      
      # Boolean fields
      hd_quality: true
      processed: false
      
      # List/array fields (context-dependent)
      genres: ["Action", "Sci-Fi"]
```

**Variable Expansion:**
- `{{now}}` → `2024-01-15T14:30:00Z` (current timestamp)
- `{{date}}` → `2024-01-15` (current date)
- `{{filename}}` → Current filename being processed
- `{{directory}}` → Current directory name

### 3. Field Templates
Reusable field update bundles:

```yaml
# Define templates
field_templates:
  - name: basic_metadata
    description: "Standard metadata updates"
    fields:
      updated: "{{now}}"
      editor: "NFO Editor v2.0"
      source: "manual"
  
  - name: quality_info
    description: "Video quality standardization"
    fields:
      source: "BluRay"
      codec: "H.264"
      resolution: "1080p"
      
# Use in profiles
profiles:
  - name: movie_standardization
    directories: [movies]
    field_templates: [basic_metadata, quality_info]  # Apply both
    field_updates:
      # Additional profile-specific updates
      studio: "Various"
```

### 4. File Patterns
Control which files are processed:

```yaml
profiles:
  - name: movie_files
    directories: [movies]
    patterns: 
      - "*movie*.nfo"     # Files containing "movie"
      - "*film*.xml"      # XML files containing "film"
      - "*.nfo"           # All .nfo files
      
  - name: tv_episodes
    directories: [tv]
    patterns:
      - "*episode*.nfo"
      - "*[Ss][0-9][0-9][Ee][0-9][0-9]*"  # S01E01 format
      - "*season*/*"      # Files in season directories
```

### 5. Scan Options Override
Customize file discovery behavior:

```yaml
profiles:
  - name: deep_scan
    directories: [movies]
    scan_options:
      pattern: "*.xml"           # Override default pattern
      recursive: true            # Scan subdirectories
      max_depth: 5               # Limit depth
      follow_symlinks: false     # Don't follow symlinks
      ignore_patterns:           # Skip these patterns
        - "*sample*"
        - "*trailer*"
        - ".*"                   # Hidden files
```

### 6. Edit Options Override
Customize file modification behavior:

```yaml
profiles:
  - name: safe_editing
    directories: [movies]
    edit_options:
      backup: true                    # Always create backups
      backup_dir: "/backups/nfo"     # Custom backup location
      preserve_format: true           # Keep original format
      max_files: 100                  # Safety limit
      dry_run_default: true           # Preview by default
```

## 🏭 Real-World Profile Examples

### Media Server Maintenance
```yaml
profiles:
  - name: monthly_cleanup
    description: "Monthly maintenance of all media files"
    directories: [movies, tv, music]
    
    field_templates: [maintenance_metadata]
    
    field_updates:
      last_maintenance: "{{now}}"
      maintenance_version: "2.0"
      
    scan_options:
      recursive: true
      ignore_patterns: ["*sample*", "*trailer*", "*.tmp"]
      
    edit_options:
      backup: true
      backup_dir: "/backups/maintenance"
      max_files: 1000
```

### New Content Processing
```yaml
profiles:
  - name: new_acquisitions
    description: "Process newly downloaded content"
    directories: [incoming, processing]
    
    field_updates:
      acquisition_date: "{{now}}"
      status: "new"
      processed: false
      quality_check: "pending"
      
    patterns: ["*.nfo", "*.xml"]
    
    edit_options:
      backup: true
      max_files: 50  # Process in small batches
```

### Quality Assurance Workflow
```yaml
profiles:
  - name: quality_check
    description: "QA workflow for media files"
    directories: [movies, tv]
    
    field_updates:
      qa_date: "{{now}}"
      qa_version: "2.0"
      quality_verified: true
      
    scan_options:
      # Only files modified in last 7 days (would need custom implementation)
      recursive: true
      
    edit_options:
      backup: true
      preserve_format: true
      max_files: 200
```

### Format Standardization
```yaml
profiles:
  - name: xml_conversion
    description: "Convert all NFO files to XML format"
    directories: [movies, tv]
    
    field_updates:
      converted_date: "{{now}}"
      original_format: "preserved_in_metadata"
      
    edit_options:
      backup: true
      output_format: xml          # Convert to XML
      preserve_format: false      # Allow format change
```

### Bulk Metadata Updates
```yaml
profiles:
  - name: studio_correction
    description: "Fix common studio name variations"
    directories: [movies]
    
    # This would need conditional logic (future feature)
    field_updates:
      studio: "Universal Pictures"  # For specific cases
      corrected_date: "{{now}}"
      
    patterns: ["*universal*.nfo"]  # Target specific files
    
    edit_options:
      backup: true
      dry_run_default: true  # Always preview first
```

## 🎬 Profile Usage Patterns

### 1. Interactive Workflow
```bash
# Launch interactive mode with profile loaded
nfo-editor --profile movie_cleanup

# The profile settings are available in the TUI:
# - Pre-selected directories
# - Pre-filled field updates
# - Applied scan/edit options
```

### 2. CLI Operations
```bash
# Use profile for specific operations
nfo-editor --profile tv_episodes --scan
nfo-editor --profile movie_cleanup --edit /media/movies
nfo-editor --profile quality_check --load movie.nfo

# Override profile settings
nfo-editor --profile bulk_update --max-files 10 --dry-run
```

### 3. Configuration-Only Execution
```bash
# Profile defines everything - just execute
nfo-editor --profile automated_maintenance

# Equivalent to complex command:
# nfo-editor --edit /media/movies /media/tv \
#   --set updated="2024-01-15" processed=true \
#   --backup --max-files 1000
```

### 4. Environment Integration
```bash
# Override profile behavior with environment
NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=true nfo-editor --profile risky_operation

# Use different backup location
NFO_EDITOR_EDIT_BACKUP_DIR=/tmp/backups nfo-editor --profile bulk_edit
```

## 🔧 Advanced Profile Techniques

### Profile Composition
Build complex profiles from simpler templates:

```yaml
# Base templates
field_templates:
  - name: timestamp_update
    fields:
      updated: "{{now}}"
      processed_by: "NFO Editor"
  
  - name: quality_metadata  
    fields:
      source: "BluRay"
      codec: "H.264"
      
# Composed profiles
profiles:
  - name: movie_processing
    directories: [movies]
    field_templates: [timestamp_update, quality_metadata]
    field_updates:
      # Additional movie-specific updates
      type: "movie"
      
  - name: tv_processing
    directories: [tv] 
    field_templates: [timestamp_update]  # Reuse timestamp
    field_updates:
      # TV-specific updates
      type: "episode"
      format: "TV Series"
```

### Conditional Profiles (Future Feature)
```yaml
# Conceptual - would require implementation
profiles:
  - name: smart_studio_fix
    directories: [movies]
    conditions:
      # Apply different updates based on existing values
      - if: "studio contains 'Universal'"
        field_updates:
          studio: "Universal Pictures"
      - if: "studio contains 'Disney'"
        field_updates:
          studio: "Walt Disney Pictures"
```

### Environment-Specific Profiles
```yaml
profiles:
  # Production environment
  - name: production_maintenance
    directories: [movies, tv]
    edit_options:
      backup: true
      backup_dir: "/prod/backups"
      max_files: 100
      
  # Development environment  
  - name: dev_testing
    directories: [test_data]
    edit_options:
      backup: false      # Skip backups in dev
      max_files: 5       # Small batches
      dry_run_default: true
```

## 🔍 Profile Validation

### Validation Commands
```bash
# Validate all profiles in configuration
nfo-editor --validate-config

# List profiles to verify they're recognized  
nfo-editor --list-profiles

# Test profile without making changes
nfo-editor --profile my_profile --dry-run
```

### Common Profile Errors

#### 1. Invalid Directory References
```yaml
# ERROR: 'unknown_dir' not defined in directories section
profiles:
  - name: test
    directories: [unknown_dir]
```

**Solution:** Add directory to configuration:
```yaml
directories:
  unknown_dir: /path/to/directory
```

#### 2. Invalid Field Template References  
```yaml
# ERROR: 'missing_template' not defined in field_templates
profiles:
  - name: test
    field_templates: [missing_template]
```

**Solution:** Define the template:
```yaml
field_templates:
  - name: missing_template
    fields:
      example: value
```

#### 3. Conflicting Options
```yaml
profiles:
  - name: conflicted
    edit_options:
      preserve_format: true
      output_format: json  # Conflicts with preserve_format
```

**Solution:** Choose one approach:
```yaml
edit_options:
  preserve_format: false  # Allow format change
  output_format: json
```

## 📊 Profile Management Best Practices

### 1. Naming Conventions
- **Descriptive names**: `movie_cleanup` not `profile1`
- **Action-oriented**: `standardize_tv_episodes`
- **Environment prefixes**: `prod_maintenance`, `dev_testing`

### 2. Documentation
```yaml
profiles:
  - name: complex_workflow
    description: |
      Comprehensive processing workflow that:
      - Standardizes metadata format
      - Updates quality information  
      - Creates timestamped backups
      - Applies studio corrections
      
      Used by: Media team for new content
      Frequency: Weekly
      Safety: Always uses backup
```

### 3. Safety First
```yaml
profiles:
  - name: safe_profile
    # Always enable backups for destructive operations
    edit_options:
      backup: true
      backup_dir: "/safe/backups"
      dry_run_default: true  # Preview by default
      max_files: 100         # Reasonable limits
```

### 4. Modular Design
Create small, focused profiles rather than monolithic ones:

```yaml
# Good: Focused profiles
profiles:
  - name: add_timestamps
    field_updates:
      updated: "{{now}}"
      
  - name: fix_studios
    field_updates:
      studio: "Universal Pictures"
      
  - name: quality_metadata
    field_templates: [quality_info]
    
# Usage: Combine as needed
# nfo-editor --profile add_timestamps
# nfo-editor --profile fix_studios  
# nfo-editor --profile quality_metadata
```

### 5. Version Control
Keep profiles in version control and document changes:

```yaml
# profiles-v2.yaml
version: "2.0"
# Changelog:
# v2.0: Added quality_metadata profile
# v1.1: Updated movie_cleanup with new fields
# v1.0: Initial profiles

profiles:
  # ... your profiles
```

## 🚀 Profile Automation

### Cron Job Integration
```bash
#!/bin/bash
# /etc/cron.daily/nfo-maintenance

export NFO_EDITOR_DEFAULT_MODE=cli
export NFO_EDITOR_RICH_SHOW_PROGRESS=false

# Run maintenance profiles
nfo-editor --profile daily_cleanup
nfo-editor --profile quality_check --max-files 50

# Generate report
nfo-editor --scan /media --format json > /var/log/nfo-daily-report.json
```

### CI/CD Integration
```yaml
# .github/workflows/media-processing.yml
name: Media Processing
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  process-media:
    runs-on: self-hosted
    steps:
      - name: Process new content
        run: |
          export NFO_EDITOR_DEFAULT_MODE=cli
          nfo-editor --profile new_acquisitions --dry-run
          nfo-editor --profile quality_assurance
```

## 🔗 Next Steps

- **[📋 Configuration Guide](configuration.md)** - Complete configuration reference
- **[🌍 Environment Variables](environment.md)** - Environment integration
- **[⚡ CLI Commands](cli-commands.md)** - Using profiles with CLI commands

---

Master profiles to transform NFO Editor from a simple tool into a powerful workflow automation system for your media management needs!
