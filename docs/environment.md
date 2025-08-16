# 🌍 Environment Variables

Complete guide to using environment variables with NFO Editor for configuration overrides, CI/CD integration, and temporary settings.

## 🎯 Overview

Environment variables provide a powerful way to:
- **Override configuration settings** without modifying files
- **Integrate with CI/CD** pipelines and automation
- **Apply temporary settings** for specific operations
- **Configure headless environments** and scripts
- **Set defaults** for different deployment environments

## 🚀 Quick Start

### Basic Usage
```bash
# Override theme temporarily
NFO_EDITOR_RICH_THEME=monokai nfo-editor --scan /media

# Disable progress bars for scripting
NFO_EDITOR_RICH_SHOW_PROGRESS=false nfo-editor --edit /media --set year=2024

# Force CLI mode
NFO_EDITOR_DEFAULT_MODE=cli nfo-editor
```

### Multiple Overrides
```bash
# Set multiple variables
export NFO_EDITOR_RICH_THEME=dark
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_MAX_FILES=50

# Use with any command
nfo-editor --profile movie_cleanup
```

## 📋 Variable Naming Convention

### Format Pattern
```
NFO_EDITOR_<SECTION>_<SETTING>=<VALUE>
```

### Examples
```bash
# Configuration mapping
NFO_EDITOR_DEFAULT_MODE=cli           # default_mode: cli
NFO_EDITOR_RICH_THEME=monokai         # rich.theme: monokai  
NFO_EDITOR_RICH_SHOW_PROGRESS=false   # rich.show_progress: false
NFO_EDITOR_SCAN_PATTERN="*.xml"       # scan.pattern: "*.xml"
NFO_EDITOR_EDIT_BACKUP=true           # edit.backup: true
NFO_EDITOR_EDIT_MAX_FILES=100         # edit.max_files: 100
```

### Nested Configuration
For nested YAML configuration, use underscores to represent hierarchy:

```yaml
# YAML Configuration
rich:
  theme: auto
  show_progress: true
scan:
  max_depth: 5
edit:
  backup_dir: /backups
```

```bash
# Environment Variables
NFO_EDITOR_RICH_THEME=monokai
NFO_EDITOR_RICH_SHOW_PROGRESS=false
NFO_EDITOR_SCAN_MAX_DEPTH=3
NFO_EDITOR_EDIT_BACKUP_DIR="/tmp/backups"
```

## 🔧 Variable Categories

### 1. Application Behavior
```bash
# Default operating mode
NFO_EDITOR_DEFAULT_MODE=interactive    # or 'cli'

# Environment prefix (advanced)
NFO_EDITOR_ENV_PREFIX="CUSTOM_"
```

### 2. Rich Display Settings
```bash
# Theme selection
NFO_EDITOR_RICH_THEME=auto            # auto, dark, light, monokai

# Progress bars
NFO_EDITOR_RICH_SHOW_PROGRESS=true    # true/false

# Color output
NFO_EDITOR_RICH_COLOR_OUTPUT=auto     # auto, always, never

# Table styling  
NFO_EDITOR_RICH_TABLE_STYLE=rounded   # rounded, heavy, double, simple, minimal

# Content preview limits
NFO_EDITOR_RICH_MAX_CONTENT_PREVIEW=2000  # 100-10000

# Syntax highlighting
NFO_EDITOR_RICH_SYNTAX_HIGHLIGHTING=true  # true/false
```

### 3. File Scanning Options
```bash
# Default file pattern
NFO_EDITOR_SCAN_PATTERN="*.nfo"       # or "*.xml", "*movie*.nfo"

# Directory traversal
NFO_EDITOR_SCAN_RECURSIVE=true        # true/false
NFO_EDITOR_SCAN_MAX_DEPTH=null        # null or 1-20
NFO_EDITOR_SCAN_FOLLOW_SYMLINKS=false # true/false
```

### 4. File Editing Settings
```bash
# Backup behavior
NFO_EDITOR_EDIT_BACKUP=true                    # true/false  
NFO_EDITOR_EDIT_BACKUP_DIR="/custom/backups"  # directory path

# Output format handling
NFO_EDITOR_EDIT_OUTPUT_FORMAT=xml              # xml, json, text, null
NFO_EDITOR_EDIT_PRESERVE_FORMAT=true           # true/false

# Safety limits
NFO_EDITOR_EDIT_MAX_FILES=1000                 # number or null
NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=false          # true/false
```

### 5. Logging Configuration
```bash
# Log level
NFO_EDITOR_LOGGING_LEVEL=INFO         # DEBUG, INFO, WARNING, ERROR

# Log file
NFO_EDITOR_LOGGING_FILE="/var/log/nfo-editor.log"  # path or null

# Log rotation
NFO_EDITOR_LOGGING_MAX_SIZE_MB=10      # 1-1000
NFO_EDITOR_LOGGING_BACKUP_COUNT=3     # 1-10
```

## 🔄 Type Conversion

Environment variables are automatically converted to appropriate types:

### Boolean Values
```bash
# All these are equivalent to `true`
NFO_EDITOR_EDIT_BACKUP=true
NFO_EDITOR_EDIT_BACKUP=True  
NFO_EDITOR_EDIT_BACKUP=1
NFO_EDITOR_EDIT_BACKUP=yes
NFO_EDITOR_EDIT_BACKUP=on

# All these are equivalent to `false`
NFO_EDITOR_EDIT_BACKUP=false
NFO_EDITOR_EDIT_BACKUP=False
NFO_EDITOR_EDIT_BACKUP=0
NFO_EDITOR_EDIT_BACKUP=no
NFO_EDITOR_EDIT_BACKUP=off
```

### Numeric Values
```bash
# Integer values
NFO_EDITOR_EDIT_MAX_FILES=100          # → 100 (int)
NFO_EDITOR_LOGGING_BACKUP_COUNT=5      # → 5 (int)

# Float values  
NFO_EDITOR_RICH_MAX_CONTENT_PREVIEW=1500.5  # → 1500.5 (float)
```

### String Values
```bash
# Quoted strings (quotes are optional but recommended for clarity)
NFO_EDITOR_RICH_THEME="monokai"
NFO_EDITOR_SCAN_PATTERN="*movie*.nfo"
NFO_EDITOR_EDIT_BACKUP_DIR="/path/with spaces/backups"
```

### Null Values
```bash
# Set to null/None
NFO_EDITOR_EDIT_BACKUP_DIR=""          # Empty string
NFO_EDITOR_EDIT_OUTPUT_FORMAT=null     # Explicit null
```

## 🎬 Usage Scenarios

### 1. Development Environment
```bash
#!/bin/bash
# dev-env.sh - Development environment setup

export NFO_EDITOR_DEFAULT_MODE=interactive
export NFO_EDITOR_RICH_THEME=monokai
export NFO_EDITOR_RICH_SHOW_PROGRESS=true
export NFO_EDITOR_LOGGING_LEVEL=DEBUG
export NFO_EDITOR_LOGGING_FILE="./dev-debug.log"
export NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=true
export NFO_EDITOR_EDIT_MAX_FILES=5

echo "Development environment configured"
nfo-editor
```

### 2. Production Automation
```bash
#!/bin/bash
# production-batch.sh - Production batch processing

export NFO_EDITOR_DEFAULT_MODE=cli
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_RICH_COLOR_OUTPUT=never
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_BACKUP_DIR="/prod/backups/nfo"
export NFO_EDITOR_EDIT_MAX_FILES=500
export NFO_EDITOR_LOGGING_LEVEL=INFO
export NFO_EDITOR_LOGGING_FILE="/var/log/nfo-batch.log"

# Process media files
nfo-editor --profile production_cleanup
```

### 3. CI/CD Pipeline
```bash
#!/bin/bash
# ci-validation.sh - CI/CD validation script

export NFO_EDITOR_DEFAULT_MODE=cli
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_RICH_COLOR_OUTPUT=never
export NFO_EDITOR_EDIT_BACKUP=false
export NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=true

# Validate NFO files without making changes
nfo-editor --scan /media --format json > nfo-report.json
nfo-editor --validate-config
```

### 4. Testing Environment
```bash
#!/bin/bash
# test-env.sh - Testing environment

export NFO_EDITOR_DEFAULT_MODE=cli
export NFO_EDITOR_RICH_THEME=auto
export NFO_EDITOR_LOGGING_LEVEL=DEBUG
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_BACKUP_DIR="./test-backups"
export NFO_EDITOR_EDIT_MAX_FILES=10
export NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=true

# Run tests
nfo-editor --profile test_profile --edit ./test-data
```

## 🔧 Integration Examples

### Docker Environment
```dockerfile
# Dockerfile
FROM python:3.12-slim

RUN pip install nfo-editor

# Set environment defaults
ENV NFO_EDITOR_DEFAULT_MODE=cli
ENV NFO_EDITOR_RICH_SHOW_PROGRESS=false
ENV NFO_EDITOR_RICH_COLOR_OUTPUT=never
ENV NFO_EDITOR_EDIT_BACKUP=true
ENV NFO_EDITOR_LOGGING_LEVEL=INFO

ENTRYPOINT ["nfo-editor"]
```

```bash
# Override at runtime
docker run -e NFO_EDITOR_RICH_THEME=dark \
           -e NFO_EDITOR_EDIT_MAX_FILES=100 \
           -v /media:/media \
           nfo-editor --scan /media
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  nfo-processor:
    image: nfo-editor:latest
    environment:
      - NFO_EDITOR_DEFAULT_MODE=cli
      - NFO_EDITOR_RICH_SHOW_PROGRESS=false
      - NFO_EDITOR_EDIT_BACKUP=true
      - NFO_EDITOR_EDIT_BACKUP_DIR=/backups
      - NFO_EDITOR_LOGGING_FILE=/logs/nfo-editor.log
    volumes:
      - /media:/media
      - ./backups:/backups
      - ./logs:/logs
    command: ["--profile", "automated_cleanup"]
```

### GitHub Actions
```yaml
# .github/workflows/nfo-validation.yml
name: NFO Validation

on:
  push:
    paths: ['media/**/*.nfo', 'media/**/*.xml']

jobs:
  validate-nfo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install NFO Editor
        run: pip install nfo-editor
        
      - name: Validate NFO files
        env:
          NFO_EDITOR_DEFAULT_MODE: cli
          NFO_EDITOR_RICH_SHOW_PROGRESS: false
          NFO_EDITOR_RICH_COLOR_OUTPUT: never
          NFO_EDITOR_LOGGING_LEVEL: INFO
        run: |
          # Scan and validate
          nfo-editor --scan ./media --format json > nfo-report.json
          nfo-editor --validate-config
          
          # Check for issues
          if [ $(jq '.errors | length' nfo-report.json) -gt 0 ]; then
            echo "NFO validation failed"
            exit 1
          fi
```

### Systemd Service
```ini
# /etc/systemd/system/nfo-processor.service
[Unit]
Description=NFO File Processor
After=network.target

[Service]
Type=oneshot
User=media
WorkingDirectory=/opt/nfo-processor

# Environment variables
Environment="NFO_EDITOR_DEFAULT_MODE=cli"
Environment="NFO_EDITOR_RICH_SHOW_PROGRESS=false"
Environment="NFO_EDITOR_EDIT_BACKUP=true"
Environment="NFO_EDITOR_EDIT_BACKUP_DIR=/var/backups/nfo"
Environment="NFO_EDITOR_LOGGING_FILE=/var/log/nfo-processor.log"

ExecStart=/usr/local/bin/nfo-editor --profile daily_maintenance

[Install]
WantedBy=multi-user.target
```

### Cron Jobs
```bash
# /etc/cron.d/nfo-maintenance
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Environment variables for cron
NFO_EDITOR_DEFAULT_MODE=cli
NFO_EDITOR_RICH_SHOW_PROGRESS=false
NFO_EDITOR_RICH_COLOR_OUTPUT=never
NFO_EDITOR_EDIT_BACKUP=true
NFO_EDITOR_LOGGING_FILE=/var/log/nfo-cron.log

# Daily maintenance at 2 AM
0 2 * * * media nfo-editor --profile daily_cleanup

# Weekly full scan on Sundays at 3 AM  
0 3 * * 0 media nfo-editor --profile weekly_full_scan
```

## 🔍 Validation and Debugging

### Check Current Environment
```bash
# Show all NFO_EDITOR_ variables
env | grep NFO_EDITOR_ | sort

# Show specific variable
echo "Theme: $NFO_EDITOR_RICH_THEME"
echo "Backup: $NFO_EDITOR_EDIT_BACKUP"
```

### Test Configuration
```bash
# Test with temporary environment
NFO_EDITOR_LOGGING_LEVEL=DEBUG NFO_EDITOR_RICH_THEME=monokai nfo-editor --validate-config

# Verify variable parsing
NFO_EDITOR_EDIT_MAX_FILES=invalid nfo-editor --validate-config
```

### Debug Environment Issues
```bash
# Enable debug logging to see variable parsing
NFO_EDITOR_LOGGING_LEVEL=DEBUG nfo-editor --scan /media --format table

# Check configuration with environment overrides
NFO_EDITOR_RICH_THEME=test_invalid nfo-editor --validate-config
```

## 📋 Common Patterns

### 1. Script-Friendly Settings
```bash
export NFO_EDITOR_DEFAULT_MODE=cli
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_RICH_COLOR_OUTPUT=never
export NFO_EDITOR_LOGGING_LEVEL=WARNING
```

### 2. Interactive Development
```bash
export NFO_EDITOR_DEFAULT_MODE=interactive  
export NFO_EDITOR_RICH_THEME=monokai
export NFO_EDITOR_RICH_SYNTAX_HIGHLIGHTING=true
export NFO_EDITOR_LOGGING_LEVEL=DEBUG
export NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=true
```

### 3. Safe Production Operations
```bash
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_BACKUP_DIR="/secure/backups"
export NFO_EDITOR_EDIT_MAX_FILES=100
export NFO_EDITOR_EDIT_DRY_RUN_DEFAULT=false
export NFO_EDITOR_LOGGING_LEVEL=INFO
export NFO_EDITOR_LOGGING_FILE="/var/log/nfo-production.log"
```

### 4. High-Volume Processing
```bash
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_RICH_COLOR_OUTPUT=never
export NFO_EDITOR_EDIT_BACKUP=true
export NFO_EDITOR_EDIT_MAX_FILES=1000
export NFO_EDITOR_LOGGING_LEVEL=WARNING
```

## 🚨 Security Considerations

### 1. Sensitive Information
```bash
# Avoid putting sensitive data in environment variables
# BAD: NFO_EDITOR_DATABASE_PASSWORD=secret123

# Instead, use configuration files with proper permissions
# Or use secrets management systems
```

### 2. Path Validation
```bash
# Be careful with paths in shared environments
NFO_EDITOR_EDIT_BACKUP_DIR="/tmp/backups"  # May be world-writable
NFO_EDITOR_LOGGING_FILE="/tmp/app.log"     # May be accessible to others

# Better:
NFO_EDITOR_EDIT_BACKUP_DIR="/var/backups/nfo"  # Controlled permissions
NFO_EDITOR_LOGGING_FILE="/var/log/nfo.log"     # Proper log directory
```

### 3. Container Security
```yaml
# Docker Compose - avoid secrets in environment
version: '3.8'
services:
  nfo-processor:
    image: nfo-editor:latest
    environment:
      - NFO_EDITOR_DEFAULT_MODE=cli
      # Don't put sensitive data here
    volumes:
      - /secure/config:/config:ro  # Mount config files instead
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Variables Not Taking Effect
```bash
# Check variable is set
echo $NFO_EDITOR_RICH_THEME

# Check correct naming
env | grep NFO_EDITOR | grep -i theme

# Validate configuration
NFO_EDITOR_LOGGING_LEVEL=DEBUG nfo-editor --validate-config
```

#### 2. Type Conversion Problems
```bash
# Invalid boolean value
NFO_EDITOR_EDIT_BACKUP=maybe  # Should be true/false

# Invalid numeric value
NFO_EDITOR_EDIT_MAX_FILES=unlimited  # Should be number or null

# Debug with validation
NFO_EDITOR_EDIT_MAX_FILES=invalid nfo-editor --validate-config
```

#### 3. Path Issues
```bash
# Relative paths may not work as expected
NFO_EDITOR_EDIT_BACKUP_DIR=./backups  # May resolve from unexpected location

# Use absolute paths
NFO_EDITOR_EDIT_BACKUP_DIR=/full/path/to/backups

# Or use ~ for home directory
NFO_EDITOR_EDIT_BACKUP_DIR=~/nfo-backups
```

#### 4. Shell Escaping
```bash
# Paths with spaces need quotes
NFO_EDITOR_EDIT_BACKUP_DIR="/path with spaces/backups"

# Special characters need escaping
NFO_EDITOR_SCAN_PATTERN="*[Mm]ovie*.nfo"
```

## 🔗 Next Steps

- **[📋 Configuration Guide](configuration.md)** - YAML configuration system
- **[🔧 Profile Management](profiles.md)** - Profile workflows and environment integration
- **[⚡ CLI Commands](cli-commands.md)** - Using environment variables with CLI
- **[🧪 Development Guide](development.md)** - Development environment setup

---

Environment variables provide flexible configuration management for NFO Editor across different deployment scenarios and automation workflows!
