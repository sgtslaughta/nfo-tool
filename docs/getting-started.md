# 📖 Getting Started with NFO Editor v2.0

Welcome to NFO Editor v2.0! This guide will help you get up and running with the modern, interactive-first NFO file management tool.

## 🚀 Quick Installation

### Option 1: Using uv (Recommended)
```bash
# Install NFO Editor
uv add nfo-editor

# Launch immediately
uv run nfo-editor
```

### Option 2: Using pip
```bash
# Install from PyPI
pip install nfo-editor

# Launch the interface
nfo-editor
```

### Option 3: Development Setup
```bash
# Clone and setup for development
git clone https://github.com/your-username/nfo-editor.git
cd nfo-editor
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## 🎮 Your First Launch

### Interactive Mode (Default)
Simply run:
```bash
nfo-editor
```

This launches the **interactive TUI interface** where you can:
- Browse directories visually
- Preview NFO files with syntax highlighting
- Edit files with guided forms
- Manage configurations through menus

### CLI Mode for Quick Tasks
Use flags for direct CLI operations:
```bash
# Scan a directory
nfo-editor --scan /media/movies

# Detect file format
nfo-editor --detect /media/movie.nfo

# Edit files with field updates
nfo-editor --edit /media/tv --set genre=Drama year=2024
```

## 🎯 Essential Commands

### Discovery Commands
```bash
# See where NFO Editor looks for config files
nfo-editor --show-config-locations

# Generate a configuration template
nfo-editor --generate-config > ~/.nfo-editor.yaml

# Get comprehensive help
nfo-editor --help
```

### File Operations
```bash
# Scan directories for NFO files
nfo-editor --scan /media/movies /media/tv

# Detect format with confidence scoring
nfo-editor --detect /path/to/file.nfo

# Load and display file contents
nfo-editor --load /path/to/file.nfo --fields title,year,genre

# Edit files safely with backups
nfo-editor --edit /media/movies --set studio="Universal" --backup
```

### Preview and Safety
```bash
# Preview changes without applying them
nfo-editor --edit /media/tv --set rating=9.0 --dry-run

# Limit the number of files processed
nfo-editor --edit /media/movies --set year=2024 --max-files 10
```

## 📋 Your First Configuration

### Generate Template
```bash
nfo-editor --generate-config > ~/.nfo-editor.yaml
```

### Basic Configuration
Edit `~/.nfo-editor.yaml`:
```yaml
version: "2.0"
default_mode: interactive

# Define your media directories
directories:
  movies: /media/movies
  tv: /media/tv-shows
  music: /media/music

# Set display preferences  
rich:
  theme: auto                # auto, dark, light, monokai
  show_progress: true       # Show progress bars
  syntax_highlighting: true # Highlight file contents

# Safe editing defaults
edit:
  backup: true             # Always create backups
  preserve_format: true    # Keep original file format
  max_files: 1000         # Safety limit
```

### Create Your First Profile
Add to your configuration:
```yaml
profiles:
  - name: my_movies
    description: "Process my movie collection"
    directories: [movies]    # Reference the movies directory above
    field_updates:
      updated: "{{now}}"     # Use current timestamp
      source: "Personal"
    patterns: ["*.nfo"]
```

### Use Your Profile
```bash
# List available profiles
nfo-editor --list-profiles

# Use your profile
nfo-editor --profile my_movies --scan
```

## 🎨 Exploring Rich Features

### Beautiful Output
```bash
# Professional table output
nfo-editor --scan /media/movies --format table

# Different themes
nfo-editor --theme monokai --detect movie.nfo
nfo-editor --theme dark --load episode.nfo
```

### Content Preview
```bash
# Load file with syntax highlighting
nfo-editor --load /media/movie.xml

# Show specific fields only
nfo-editor --load /media/movie.nfo --fields title,year,genre,plot
```

### Progress Tracking
```bash
# See progress bars for batch operations
nfo-editor --edit /media/movies --set studio="Universal"

# Multi-directory scan with progress
nfo-editor --scan /media/movies /media/tv /media/music
```

## 🌍 Environment Integration

### Override Settings
```bash
# Change theme temporarily
NFO_EDITOR_RICH_THEME=monokai nfo-editor --scan /media

# Disable progress bars for scripting
NFO_EDITOR_RICH_SHOW_PROGRESS=false nfo-editor --edit /media --set year=2024

# Force CLI mode
NFO_EDITOR_DEFAULT_MODE=cli nfo-editor
```

### Scripting Integration
```bash
#!/bin/bash
# movie-update.sh

# Set environment for batch processing
export NFO_EDITOR_RICH_SHOW_PROGRESS=false
export NFO_EDITOR_EDIT_BACKUP=true

# Process movies
nfo-editor --edit /media/movies --set updated="$(date)" --max-files 100

# Generate report
nfo-editor --scan /media/movies --format json > movie-report.json
```

## 🔧 Configuration Discovery

NFO Editor searches for configuration files in this order:

1. `./nfo-editor.yaml` (current directory)
2. `./.nfo-editor.yaml` (current directory, hidden)
3. `~/.nfo-editor.yaml` (home directory)
4. `~/.config/nfo-editor/config.yaml` (XDG config)
5. Custom path via `--config <path>`

### Validation
```bash
# Validate your configuration
nfo-editor --validate-config

# Check specific configuration file
nfo-editor --config /path/to/config.yaml --validate-config
```

## 📚 Next Steps

Now that you're up and running:

- **[🎮 Interactive Mode Guide](interactive-mode.md)** - Master the TUI interface
- **[⚡ CLI Commands Reference](cli-commands.md)** - Learn all available commands
- **[📋 Configuration Deep Dive](configuration.md)** - Advanced configuration features
- **[🔧 Profile Management](profiles.md)** - Create powerful reusable workflows
- **[🎨 Themes and Formatting](themes.md)** - Customize the visual experience

## 🆘 Getting Help

### Built-in Help
```bash
nfo-editor --help                    # Main help
nfo-editor --generate-config        # Configuration template  
nfo-editor --show-config-locations  # Config file locations
```

### Common Issues

**Command not found:**
```bash
# Make sure it's installed
pip show nfo-editor

# Or use uv
uv run nfo-editor
```

**Configuration errors:**
```bash
# Validate your config
nfo-editor --validate-config

# Check config locations
nfo-editor --show-config-locations
```

**Permission issues:**
```bash
# Run with dry-run first
nfo-editor --edit /media --set test=value --dry-run

# Check file permissions
ls -la /media/
```

## 💡 Pro Tips

1. **Start with interactive mode** to explore your NFO files visually
2. **Use `--dry-run` first** when editing to preview changes
3. **Create profiles** for common tasks to save time
4. **Use environment variables** for temporary overrides
5. **Generate config templates** to see all available options
6. **Validate configurations** before using them in production

---

Ready to dive deeper? Check out the [Interactive Mode Guide](interactive-mode.md) or explore the [CLI Commands Reference](cli-commands.md)!
