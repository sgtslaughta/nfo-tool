# NFO Editor v2.0 - Modern NFO File Manager

A comprehensive **interactive-first** CLI tool and Python library for parsing and editing .nfo files in various formats. Built with modern terminal UI, comprehensive configuration management, and enterprise-grade features.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rich Terminal UI](https://img.shields.io/badge/UI-Rich%20Terminal-purple.svg)](https://rich.readthedocs.io/)

## ✨ What's New in v2.0

🎮 **Interactive-First Design** - Beautiful TUI interface launches by default  
🎨 **Professional Terminal Output** - Progress bars, syntax highlighting, and themes  
⚙️ **Enterprise Configuration** - YAML configs with profiles and validation  
🌍 **Environment Integration** - Override any setting with environment variables  
📋 **Profile Workflows** - Reusable configurations for common tasks  
🔧 **Extensible Architecture** - Designed for easy customization and expansion

## 🚀 Quick Start

### Interactive Mode (Default)
```bash
# Launch the interactive interface
nfo-editor

# Use a specific configuration
nfo-editor --config ~/my-workflow.yaml
```

### Enhanced CLI Mode  
```bash
# Modern CLI with beautiful output
nfo-editor --scan /media/movies --format table
nfo-editor --edit /media/tv --set genre=Drama --profile tv_cleanup
nfo-editor --detect movie.nfo --theme monokai
nfo-editor --load episode.nfo --syntax-highlighting
```

### Configuration-Driven Workflows
```bash
# Generate configuration template
nfo-editor --generate-config > ~/.nfo-editor.yaml

# Run predefined workflows
nfo-editor --profile movie_cleanup
nfo-editor --config workflows.yaml --profile tv_standardize
```

## 📚 Documentation

### 🎯 Core Features
- **[📖 Getting Started Guide](docs/getting-started.md)** - Installation, first steps, and basic usage
- **[🎮 Interactive Mode](docs/interactive-mode.md)** - TUI interface and navigation
- **[⚡ CLI Commands](docs/cli-commands.md)** - Complete command reference with examples

### ⚙️ Configuration & Workflows  
- **[📋 Configuration Guide](docs/configuration.md)** - YAML configuration system
- **[🔧 Profile Management](docs/profiles.md)** - Reusable workflow configurations
- **[🌍 Environment Variables](docs/environment.md)** - Override settings via environment

### 🎨 Advanced Features
- **[🎨 Themes & Formatting](docs/themes.md)** - Terminal themes and Rich output
- **[📊 Output Formats](docs/output-formats.md)** - Table, JSON, YAML output options
- **[🔍 Format Detection](docs/format-detection.md)** - Smart NFO format recognition

### 🔧 Development & Integration
- **[🐍 Python Library API](docs/python-api.md)** - Using NFO Editor as a Python library
- **[🧩 Extending NFO Editor](docs/extending.md)** - Custom parsers, writers, and plugins
- **[🧪 Testing & Development](docs/development.md)** - Contributing and development setup

## 🎯 Core Capabilities

### 📁 **Multi-Format NFO Support**
- **XML NFO files** (Kodi/XBMC format) with full element support
- **JSON NFO files** with nested structure preservation  
- **Plain text NFO files** (key-value pairs, sections)
- **Smart format detection** with confidence scoring
- **Automatic encoding detection** (UTF-8, Latin-1, etc.)

### 🎨 **Beautiful Terminal Experience**  
- **Rich progress bars** with real-time file processing updates
- **Syntax highlighting** for XML, JSON, and text content
- **Professional tables** with metadata, file sizes, timestamps
- **Multiple themes** (auto, dark, light, monokai) with auto-detection
- **Color-coded status indicators** and error messages

### ⚙️ **Enterprise-Grade Configuration**
- **YAML configuration files** with comprehensive validation
- **Profile system** for reusable workflows and common tasks
- **Environment variable overrides** for CI/CD and scripting
- **Configuration discovery** (current dir, home, XDG paths)
- **Validation tools** with helpful error messages

### 🛡️ **Production-Ready Safety**
- **Automatic backups** with configurable backup directories
- **Dry-run mode** for safe testing and preview
- **Comprehensive error handling** with helpful suggestions
- **Batch operation limits** to prevent accidental mass changes
- **Rollback capabilities** and change tracking

## 🚀 Installation

### Using uv (Recommended)
```bash
# Install the package
uv add nfo-editor

# Run directly 
uv run nfo-editor
```

### Using pip
```bash
# Install from PyPI
pip install nfo-editor

# Launch the interface
nfo-editor
```

### Development Installation
```bash
# Clone and setup development environment
git clone https://github.com/your-username/nfo-editor.git
cd nfo-editor
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests
python -m pytest
```

## 🎮 Usage Modes

NFO Editor v2.0 provides three complementary ways to work with NFO files:

### 1. 🎮 Interactive Mode (Default)
Perfect for exploration, one-time tasks, and learning the system.

```bash
nfo-editor                    # Launch interactive TUI
nfo-editor --config my.yaml  # Launch with specific config
```

**Features:**
- Beautiful terminal interface with navigation
- Real-time file preview and editing
- Visual configuration management
- Guided workflows and help system

### 2. ⚡ Enhanced CLI Mode  
Ideal for scripting, automation, and power users.

```bash
# Modern CLI with rich output
nfo-editor --scan /media/movies --format table
nfo-editor --edit /media/tv --set genre=Drama --backup
nfo-editor --detect movie.nfo --theme monokai
nfo-editor --load episode.nfo --fields title,year,genre

# Use profiles for complex workflows
nfo-editor --profile movie_cleanup --dry-run
nfo-editor --profile tv_standardize --max-files 100
```

**Features:**
- Rich progress bars and status indicators
- Professional table output with metadata
- Syntax highlighting for file contents  
- Multiple output formats (table, JSON, YAML)
- Environment variable integration

### 3. ⚙️ Configuration-Driven Workflows
Enterprise-grade configuration management for complex scenarios.

```bash
# Configuration management
nfo-editor --generate-config > ~/.nfo-editor.yaml
nfo-editor --validate-config
nfo-editor --list-profiles
nfo-editor --show-config-locations

# Profile-based execution
nfo-editor --config workflows.yaml --profile movie_cleanup
nfo-editor --profile tv_episodes --edit /media/tv

# Environment overrides
NFO_EDITOR_RICH_THEME=dark nfo-editor --scan /media
NFO_EDITOR_EDIT_BACKUP=false nfo-editor --profile quick_update
```

**Features:**
- YAML configuration with validation
- Reusable profiles for common tasks
- Environment variable overrides
- Configuration discovery and templates

## 🎨 Rich Terminal Features

### Beautiful Output Examples

**Professional Scan Results:**
```
                  📂 Scan Summary                  
┌─────────────────────┬─────────────────────────┐
│ NFO files found     │ 1,247                   │
│ Directories scanned │ 15                      │
│ Total files scanned │ 45,892                  │
│ Scan time           │ 2.34s                   │
└─────────────────────┴─────────────────────────┘
```

**Format Detection with Confidence:**
```
╭────────── 🔍 Format Detection ──────────╮
│ File: /media/movies/inception.nfo      │
│ Format: XML                            │
│ Confidence: 🟢 98.5%                   │
│ Encoding: UTF-8                        │
╰────────────────────────────────────────╯
```

**Syntax-Highlighted Content:**
```xml
    1 <?xml version="1.0" encoding="utf-8"?>
    2 <movie>
    3     <title>Inception</title>
    4     <year>2010</year>
    5     <rating>8.8</rating>
    6 </movie>
```

## 📋 Configuration Example

Create powerful, reusable workflows with YAML configuration:

```yaml
# ~/.nfo-editor.yaml
version: "2.0"
default_mode: interactive

# Directory shortcuts
directories:
  movies: /media/movies
  tv: /media/tv-shows
  documentaries: /media/docs

# Display preferences
rich:
  theme: monokai
  show_progress: true
  syntax_highlighting: true

# Reusable profiles
profiles:
  - name: movie_cleanup
    description: "Standardize movie NFO files"
    directories: [movies]
    field_updates:
      updated: "{{now}}"
      source: "BluRay"
    patterns: ["*movie*.nfo"]
    
  - name: tv_episodes
    description: "Process TV episode files"
    directories: [tv]
    scan_options:
      pattern: "*episode*.nfo"
      max_depth: 3
    edit_options:
      backup: true
      preserve_format: true
```

## 🎯 Supported NFO Formats

NFO Editor supports three major NFO formats with intelligent detection and conversion:

### **XML Format (Kodi/XBMC)**
The standard format used by Kodi media center with full metadata support including cast, crew, ratings, and artwork information.

### **JSON Format**  
Structured JSON format ideal for modern applications and API integration, supporting nested data and arrays.

### **Plain Text Format**
Human-readable key-value format with section support, perfect for simple metadata and manual editing.

**Format Detection:** Automatic format recognition with confidence scoring  
**Encoding Support:** UTF-8, Latin-1, and other character encodings  
**Conversion:** Convert between any supported formats while preserving data

See **[🔍 Format Detection Guide](docs/format-detection.md)** for detailed format specifications and examples.

## 🏆 What's Included

NFO Editor v2.0 is a **complete modernization** with enterprise-grade features:

| Feature Category | Status | Description |
|------------------|---------|-------------|
| **🎮 Interactive TUI** | ✅ **Foundation Ready** | Interactive mode launches by default with beautiful terminal interface |
| **⚡ Modern CLI** | ✅ **Fully Implemented** | Flag-based CLI with Rich output, progress bars, and themes |
| **⚙️ Configuration System** | ✅ **Enterprise-Grade** | YAML configs with profiles, validation, and environment overrides |
| **🎨 Rich Integration** | ✅ **Production Ready** | Syntax highlighting, progress tracking, professional tables |
| **📋 Profile Management** | ✅ **Advanced Workflows** | Reusable configurations for complex automation scenarios |
| **🌍 Environment Support** | ✅ **CI/CD Ready** | Complete environment variable integration |
| **🐍 Python Library** | ✅ **Full API** | Comprehensive programmatic access to all functionality |
| **📚 Documentation** | ✅ **Comprehensive** | Complete guides for all features and use cases |

### **Three Implementation Phases Complete:**
- **✅ Phase 1**: Modern Click-based CLI architecture  
- **✅ Phase 2**: Professional Rich terminal output with themes and progress bars
- **✅ Phase 3**: Enterprise-grade YAML configuration with profiles and validation

## 🤝 Contributing

We welcome contributions! NFO Editor v2.0 provides a solid foundation for continued development.

### Quick Start for Contributors
```bash
# Clone and setup development environment
git clone https://github.com/your-username/nfo-editor.git
cd nfo-editor
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests and validation
python -m pytest
nfo-editor --validate-config
```

**See [🧪 Development Guide](docs/development.md)** for complete contributor documentation including architecture overview, testing procedures, and coding standards.

## 🎉 Success Story

NFO Editor v2.0 represents a **complete transformation** from a simple library to a modern, enterprise-ready media management tool:

### **Before v2.0** → **After v2.0**
- Basic argparse CLI → **Interactive-first TUI with professional CLI**
- Simple text output → **Rich terminal output with themes and progress bars**  
- No configuration → **Enterprise YAML configuration with profiles**
- Library-only → **Complete application with three usage modes**
- Limited documentation → **Comprehensive guides for all features**

### **Ready for Production**
NFO Editor v2.0 provides everything needed for:
- **Personal media collections** with intuitive interactive mode
- **Enterprise media processing** with configuration profiles and automation
- **Developer integration** with comprehensive Python API
- **CI/CD workflows** with environment variable support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rich Library** - For beautiful terminal output and TUI framework
- **Click Framework** - For modern command-line interface architecture  
- **Pydantic** - For robust configuration validation and data modeling
- **Kodi/XBMC Community** - For NFO format standards and inspiration
- **Modern Python Ecosystem** - uv, pytest, and development best practices

---

## 🚀 Get Started Now

```bash
# Install and launch
uv add nfo-editor && nfo-editor

# Or explore the CLI
pip install nfo-editor && nfo-editor --help
```

**Questions?** Check the **[📖 Getting Started Guide](docs/getting-started.md)** or **[submit an issue](https://github.com/your-username/nfo-editor/issues)** for support.

**NFO Editor v2.0** - *Modern media management made beautiful* ✨
