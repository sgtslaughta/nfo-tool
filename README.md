# NFO Editor

A comprehensive Python library for parsing and editing .nfo files in various formats including XML, JSON, and plain text key-value pairs.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

🎯 **Multi-Format Support**
- XML NFO files (Kodi/XBMC format)
- JSON NFO files 
- Plain text NFO files (key-value pairs, sections)

🔍 **Smart Detection**
- Automatic format detection with confidence scoring
- Character encoding detection
- Fallback format support

⚡ **Batch Operations**
- Process multiple directories recursively
- Pattern-based file filtering
- Parallel processing capabilities

🛡️ **Safe Editing**
- Automatic backup creation
- Dry-run mode for previewing changes
- Comprehensive error handling

🏗️ **Extensible Architecture**
- Modular parser and writer system
- Custom format support
- Plugin-friendly design

## Installation

### Using uv (recommended)

```bash
uv add nfo-editor
```

### Using pip

```bash
pip install nfo-editor
```

### Development Installation

```bash
git clone https://github.com/your-username/nfo-editor.git
cd nfo-editor
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Scan directories for NFO files
nfo-editor scan /media/movies /media/tv

# Edit files in a directory
nfo-editor edit /media/movies --set genre=Action year=2024

# Preview changes without applying
nfo-editor edit /media/movies --set rating=9.0 --dry-run

# Detect format of a specific file
nfo-editor detect /media/movie.nfo

# Convert files to different format
nfo-editor edit /media/movies --output-format json --backup
```

### Python Library Usage

#### Simple Batch Editing

```python
from nfo_editor import edit_nfo_files

# Edit all NFO files in directories
results = edit_nfo_files(
    directories=['/media/movies', '/media/tv'],
    field_updates={'genre': 'Action', 'year': 2024},
    backup=True
)

print(f"Successfully edited {results['successful_edits']} files")
```

#### Advanced Usage

```python
from nfo_editor import NFOEditor

# Create editor instance
editor = NFOEditor(
    directories=['/media/movies'],
    create_backups=True,
    preserve_format=True
)

# Load a specific file
nfo_data = editor.load_file('/media/movie.nfo')
print(f"Title: {nfo_data.get_field('title')}")
print(f"Year: {nfo_data.get_field('year')}")

# Edit fields
nfo_data.set_field('genre', 'Sci-Fi')
nfo_data.set_field('rating', 8.5)

# Save changes
from nfo_editor import XMLNFOWriter
writer = XMLNFOWriter()
writer.write(nfo_data, create_backup=True)
```

#### Format Detection and Parsing

```python
from nfo_editor import detect_nfo_format, load_nfo_file

# Detect file format
format_info = detect_nfo_format('/media/movie.nfo')
print(f"Format: {format_info['format']}")
print(f"Confidence: {format_info['confidence']}")

# Load and parse file
data = load_nfo_file('/media/movie.nfo')
print(f"Fields: {list(data['fields'].keys())}")
```

## Supported NFO Formats

### XML Format (Kodi/XBMC)

```xml
<?xml version="1.0" encoding="utf-8"?>
<movie>
    <title>The Matrix</title>
    <year>1999</year>
    <genre>Action</genre>
    <genre>Sci-Fi</genre>
    <plot>A computer programmer discovers reality is a simulation...</plot>
    <rating>8.7</rating>
    <cast>
        <actor>
            <name>Keanu Reeves</name>
            <role>Neo</role>
        </actor>
    </cast>
</movie>
```

### JSON Format

```json
{
  "title": "Inception",
  "year": 2010,
  "genres": ["Action", "Sci-Fi", "Thriller"],
  "plot": "A thief who steals corporate secrets...",
  "rating": 8.8,
  "cast": [
    {"name": "Leonardo DiCaprio", "role": "Dom Cobb"}
  ]
}
```

### Plain Text Format

```
Title: Blade Runner 2049
Year: 2017
Genre: Sci-Fi, Drama, Thriller
Rating: 8.0
Plot: Thirty years after the events of the first film...

[Cast]
Ryan Gosling: Officer K
Harrison Ford: Rick Deckard
```

## API Reference

### Core Classes

#### NFOEditor

Main class for coordinating NFO file operations.

```python
editor = NFOEditor(
    directories=['/path/to/media'],
    create_backups=True,
    auto_detect_format=True,
    preserve_format=True,
    default_output_format='xml'
)

# Scan for files
scan_result = editor.scan_files(pattern='*.nfo')

# Load a file
nfo_data = editor.load_file('/path/to/file.nfo')

# Edit a single file
result = editor.edit_file(
    '/path/to/file.nfo',
    {'title': 'New Title', 'year': 2024}
)

# Batch edit
batch_result = editor.batch_edit(
    {'genre': 'Action'},
    file_pattern='*movie*.nfo',
    max_files=100
)
```

#### NFOData

Container for parsed NFO file data.

```python
# Get field values
title = nfo_data.get_field('title')
nested_value = nfo_data.get_field('cast.actor.name')

# Set field values  
nfo_data.set_field('genre', 'Action')
nfo_data.set_field('metadata.updated', '2024-01-15')

# Check field existence
if nfo_data.has_field('rating'):
    print(f"Rating: {nfo_data.get_field('rating')}")

# Get all fields (flattened)
all_fields = nfo_data.get_all_fields()
```

### Convenience Functions

#### edit_nfo_files()

```python
results = edit_nfo_files(
    directories=['/media/movies'],
    field_updates={'genre': 'Action', 'year': 2024},
    backup=True,
    dry_run=False,
    file_pattern='*.nfo',
    output_format='xml',
    max_files=None
)
```

#### scan_nfo_files()

```python
results = scan_nfo_files(
    directories=['/media/movies'],
    pattern='*movie*.nfo',
    recursive=True
)
```

#### detect_nfo_format()

```python
format_info = detect_nfo_format('/path/to/file.nfo')
print(format_info['format'])        # 'xml', 'json', or 'text'
print(format_info['confidence'])    # 0.0 to 1.0
```

#### load_nfo_file()

```python
data = load_nfo_file('/path/to/file.nfo')
print(data['format_type'])          # Detected format
print(data['fields'])               # Parsed field data
print(data['all_fields_flat'])      # Flattened field dictionary
```

## Advanced Features

### Custom Parsers

```python
from nfo_editor.parsers.base import BaseNFOParser
from nfo_editor.parsers.base import NFOData

class CustomNFOParser(BaseNFOParser):
    supported_extensions = ['.custom']
    format_name = "Custom"
    
    def can_parse(self, file_path):
        # Implementation
        pass
    
    def parse(self, file_path):
        # Implementation
        return NFOData(...)

# Register custom parser
editor = NFOEditor()
editor.parsers['custom'] = CustomNFOParser()
```

### Custom Writers

```python
from nfo_editor.writers.base import BaseNFOWriter

class CustomNFOWriter(BaseNFOWriter):
    format_name = "Custom"
    default_extension = ".custom"
    
    def can_write(self, nfo_data):
        return True
    
    def write(self, nfo_data, output_path=None, create_backup=True):
        # Implementation
        pass

# Register custom writer
editor = NFOEditor()
editor.writers['custom'] = CustomNFOWriter()
```

### Filtering and Pattern Matching

```python
# Custom filter function
def my_filter(file_path):
    return 'movie' in file_path.name.lower()

scanner = NFOScanner()
files = scanner.find_files_with_filter(
    directories=['/media'],
    custom_filter=my_filter
)

# Pattern-based filtering
files = scanner.find_files_by_pattern(
    directories=['/media'],
    pattern='*[sS][0-9][0-9][eE][0-9][0-9]*'  # TV episodes
)
```

## Examples

See the `examples/` directory for complete working examples:

- `examples/demo.py` - Comprehensive demonstration
- `examples/movie.xml` - Kodi movie NFO
- `examples/movie.json` - JSON movie metadata
- `examples/movie.nfo` - Plain text movie info
- `examples/tvshow.xml` - TV show metadata
- `examples/episode.nfo` - TV episode info

## Testing

```bash
# Run basic tests
python tests/test_basic.py

# Run with verbose output
python -m unittest tests.test_basic -v
```

## Error Handling

The library provides comprehensive error handling with specific exception types:

```python
from nfo_editor import (
    NFOError,           # Base exception
    NFOParseError,      # Parsing failures
    NFOFieldError,      # Field operation errors
    NFOAccessError,     # File access issues
    NFOFormatError,     # Format not supported
)

try:
    editor = NFOEditor(directories=['/invalid/path'])
    result = editor.batch_edit({'title': 'New Title'})
except NFOAccessError as e:
    print(f"Access error: {e}")
except NFOParseError as e:
    print(f"Parse error: {e}")
except NFOError as e:
    print(f"General NFO error: {e}")
```

## Performance Tips

1. **Use pattern filtering** to reduce the number of files processed
2. **Set max_files** limit for large directories
3. **Disable backups** for read-only operations
4. **Use dry-run mode** to test changes before applying
5. **Cache parsed files** when processing multiple times

```python
# Efficient batch processing
editor = NFOEditor(
    directories=['/media/movies'],
    create_backups=False  # Disable for read-only ops
)

# Process in chunks
for chunk_files in chunks(large_file_list, 100):
    results = editor.batch_edit(
        field_updates={'updated': '2024-01-15'},
        max_files=100
    )
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/nfo-editor.git
cd nfo-editor

# Setup development environment
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run linting
black nfo_editor/
isort nfo_editor/
mypy nfo_editor/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Kodi/XBMC NFO file format
- Built with modern Python best practices
- Designed for media center and automation workflows

---

For more information, please visit the [documentation](https://github.com/your-username/nfo-editor) or [submit an issue](https://github.com/your-username/nfo-editor/issues).
