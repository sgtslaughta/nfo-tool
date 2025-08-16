# 🐍 Python Library API

Complete reference for using NFO Editor as a Python library in your own applications, scripts, and automation workflows.

## 🎯 Overview

NFO Editor provides a comprehensive Python API that allows you to:
- **Parse and manipulate** NFO files programmatically
- **Batch process** large collections of media files
- **Integrate** NFO functionality into existing applications
- **Create custom** parsers and writers for specialized formats
- **Build automation** scripts for media management

## 🚀 Quick Start

### Basic Installation and Import
```python
# Install the library
# pip install nfo-editor

# Import main functions
from nfo_editor import (
    edit_nfo_files,
    scan_nfo_files, 
    detect_nfo_format,
    load_nfo_file,
    NFOEditor
)
```

### Simple Examples

**Batch Edit Files:**
```python
from nfo_editor import edit_nfo_files

# Edit all NFO files in directories
results = edit_nfo_files(
    directories=['/media/movies', '/media/tv'],
    field_updates={'genre': 'Action', 'year': 2024},
    backup=True,
    dry_run=False
)

print(f"Successfully edited {results['successful_edits']} files")
print(f"Failed: {results['failed_edits']}")
```

**Scan and Discover:**
```python
from nfo_editor import scan_nfo_files

# Find all NFO files
results = scan_nfo_files(
    directories=['/media/movies'],
    pattern='*.nfo',
    recursive=True
)

for file_path in results['nfo_files']:
    print(f"Found: {file_path}")
```

**Format Detection:**
```python
from nfo_editor import detect_nfo_format

# Detect file format
format_info = detect_nfo_format('/media/movie.nfo')
print(f"Format: {format_info['format']}")
print(f"Confidence: {format_info['confidence']:.1%}")
```

## 📚 Core API Functions

### 1. edit_nfo_files()
Batch edit multiple NFO files with field updates.

```python
def edit_nfo_files(
    directories: List[str],
    field_updates: Dict[str, Any],
    backup: bool = True,
    dry_run: bool = False,
    file_pattern: str = "*.nfo",
    output_format: Optional[str] = None,
    max_files: Optional[int] = None
) -> Dict[str, Any]:
```

**Parameters:**
- `directories`: List of directory paths to process
- `field_updates`: Dictionary of field names and values to update
- `backup`: Create backup files before editing
- `dry_run`: Preview changes without applying them
- `file_pattern`: Glob pattern for file matching
- `output_format`: Target format ('xml', 'json', 'text', or None to preserve)
- `max_files`: Maximum number of files to process

**Returns:**
```python
{
    'successful_edits': 42,
    'failed_edits': 3, 
    'total_files_found': 45,
    'execution_time_seconds': 2.34,
    'dry_run': False,
    'backup_created': True,
    'results': [
        {
            'file_path': '/media/movie1.nfo',
            'success': True,
            'changes_made': ['title', 'year'],
            'backup_path': '/media/movie1.nfo.backup'
        },
        # ... more results
    ],
    'errors': [
        {
            'file_path': '/media/broken.nfo',
            'error': 'Parse error: Invalid XML format'
        }
    ]
}
```

**Example Usage:**
```python
# Basic field updates
results = edit_nfo_files(
    directories=['/media/movies'],
    field_updates={
        'studio': 'Universal Pictures',
        'updated': '2024-01-15T10:30:00Z',
        'rating': 8.5
    },
    backup=True
)

# Dry run to preview changes
preview = edit_nfo_files(
    directories=['/media/tv'],
    field_updates={'genre': 'Drama'},
    dry_run=True,
    max_files=5
)

for result in preview['results']:
    if result['success']:
        print(f"Would update {result['file_path']}: {result['changes_made']}")
```

### 2. scan_nfo_files()
Discover and catalog NFO files in directories.

```python
def scan_nfo_files(
    directories: List[str],
    pattern: str = "*.nfo", 
    recursive: bool = True
) -> Dict[str, Any]:
```

**Returns:**
```python
{
    'nfo_files': ['/media/movie1.nfo', '/media/movie2.xml'],
    'directories_scanned': 2,
    'total_files_scanned': 1500,
    'scan_time_seconds': 0.45,
    'pattern_used': '*.nfo',
    'recursive': True,
    'errors': []
}
```

**Example Usage:**
```python
# Comprehensive scan
results = scan_nfo_files(
    directories=['/media/movies', '/media/tv'],
    pattern='*movie*.nfo',
    recursive=True
)

print(f"Found {len(results['nfo_files'])} NFO files")
print(f"Scanned {results['total_files_scanned']} total files in {results['scan_time_seconds']:.2f}s")

# Process each found file
for file_path in results['nfo_files']:
    # Load and process file
    data = load_nfo_file(file_path)
    print(f"{file_path}: {data['fields'].get('title', 'No title')}")
```

### 3. detect_nfo_format()
Analyze and detect NFO file format with confidence scoring.

```python
def detect_nfo_format(file_path: str) -> Dict[str, Any]:
```

**Returns:**
```python
{
    'format': 'xml',           # 'xml', 'json', 'text'
    'confidence': 0.98,        # 0.0 to 1.0
    'encoding': 'utf-8',       # Detected encoding
    'fallback_formats': ['json', 'text'],  # Alternative formats
    'file_size': 2048,         # File size in bytes
    'modified': False          # Whether file was modified
}
```

**Example Usage:**
```python
import os

# Check all files in a directory
for filename in os.listdir('/media/movies'):
    if filename.endswith(('.nfo', '.xml')):
        file_path = os.path.join('/media/movies', filename)
        format_info = detect_nfo_format(file_path)
        
        print(f"{filename}:")
        print(f"  Format: {format_info['format']} ({format_info['confidence']:.1%})")
        print(f"  Encoding: {format_info['encoding']}")
```

### 4. load_nfo_file()
Load and parse NFO file contents with full metadata.

```python
def load_nfo_file(file_path: str) -> Dict[str, Any]:
```

**Returns:**
```python
{
    'file_path': '/media/movie.nfo',
    'format_type': 'xml',
    'encoding': 'utf-8',
    'fields': {
        'title': 'The Matrix',
        'year': 1999,
        'genre': ['Action', 'Sci-Fi'],
        'cast': {
            'actor': [
                {'name': 'Keanu Reeves', 'role': 'Neo'},
                {'name': 'Laurence Fishburne', 'role': 'Morpheus'}
            ]
        }
    },
    'all_fields_flat': {
        'title': 'The Matrix',
        'year': 1999,
        'cast.actor.name': 'Keanu Reeves',
        'cast.actor.role': 'Neo',
        # ... flattened field paths
    },
    'metadata': {
        'file_size': 2048,
        'modified_time': '2024-01-15T10:30:00Z',
        'parse_time_seconds': 0.02
    }
}
```

**Example Usage:**
```python
# Load and analyze file
data = load_nfo_file('/media/movie.nfo')

print(f"Title: {data['fields'].get('title')}")
print(f"Year: {data['fields'].get('year')}")
print(f"Format: {data['format_type']}")

# Access nested fields
if 'cast' in data['fields']:
    cast = data['fields']['cast']
    if 'actor' in cast:
        for actor in cast['actor']:
            print(f"Actor: {actor.get('name')} as {actor.get('role')}")

# Use flattened fields for easy access
flat_fields = data['all_fields_flat']
for field_path, value in flat_fields.items():
    print(f"{field_path}: {value}")
```

## 🏗️ Advanced API: NFOEditor Class

The `NFOEditor` class provides advanced functionality for complex workflows.

### Initialization
```python
from nfo_editor import NFOEditor

editor = NFOEditor(
    directories=['/media/movies'],
    create_backups=True,
    auto_detect_format=True,
    preserve_format=True,
    default_output_format='xml',
    max_files_per_operation=1000
)
```

### Core Methods

#### File Operations
```python
# Load a single file
nfo_data = editor.load_file('/media/movie.nfo')
print(f"Title: {nfo_data.get_field('title')}")

# Edit a single file
result = editor.edit_file(
    '/media/movie.nfo',
    {'genre': 'Sci-Fi', 'rating': 9.0}
)

# Batch operations
batch_result = editor.batch_edit(
    field_updates={'updated': '2024-01-15'},
    file_pattern='*movie*.nfo',
    max_files=100
)
```

#### Scanning and Discovery
```python
# Scan for files
scan_result = editor.scan_files(
    pattern='*.nfo',
    recursive=True
)

# Get detailed file information
file_info = editor.get_file_info('/media/movie.nfo')
print(f"Format: {file_info['format']}")
print(f"Size: {file_info['size']} bytes")
```

### NFOData Object
The `NFOData` class represents parsed NFO file data:

```python
# Get NFOData object
nfo_data = editor.load_file('/media/movie.nfo')

# Field access
title = nfo_data.get_field('title')
nested_value = nfo_data.get_field('cast.actor.name')

# Field modification
nfo_data.set_field('genre', 'Action')
nfo_data.set_field('metadata.updated', '2024-01-15')

# Field existence check
if nfo_data.has_field('rating'):
    current_rating = nfo_data.get_field('rating')
    nfo_data.set_field('rating', current_rating + 1)

# Get all fields
all_fields = nfo_data.get_all_fields()
nested_structure = nfo_data.get_nested_fields()
```

## 🔧 Custom Parsers and Writers

### Custom Parser Example
```python
from nfo_editor.parsers.base import BaseNFOParser, NFOData

class CustomNFOParser(BaseNFOParser):
    """Custom parser for specialized NFO format."""
    
    supported_extensions = ['.custom']
    format_name = "Custom"
    
    def can_parse(self, file_path: str) -> float:
        """Return confidence score (0.0-1.0) for parsing this file."""
        if file_path.endswith('.custom'):
            return 0.95
        return 0.0
    
    def parse(self, file_path: str) -> NFOData:
        """Parse the file and return NFOData object."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Custom parsing logic
        fields = self._parse_custom_format(content)
        
        return NFOData(
            file_path=file_path,
            format_type='custom',
            fields=fields,
            encoding='utf-8'
        )
    
    def _parse_custom_format(self, content: str) -> dict:
        """Implement your custom parsing logic."""
        # Your parsing implementation
        return {'title': 'Parsed Title', 'year': 2024}

# Register custom parser
editor = NFOEditor()
editor.register_parser('custom', CustomNFOParser())
```

### Custom Writer Example
```python
from nfo_editor.writers.base import BaseNFOWriter

class CustomNFOWriter(BaseNFOWriter):
    """Custom writer for specialized output format."""
    
    format_name = "Custom"
    default_extension = ".custom"
    
    def can_write(self, nfo_data) -> bool:
        """Check if this writer can handle the data."""
        return True  # Accept all data
    
    def write(self, nfo_data, output_path=None, create_backup=True):
        """Write NFO data to file."""
        if output_path is None:
            output_path = nfo_data.file_path
        
        if create_backup and os.path.exists(output_path):
            backup_path = f"{output_path}.backup"
            shutil.copy2(output_path, backup_path)
        
        # Custom writing logic
        content = self._format_custom_content(nfo_data.fields)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _format_custom_content(self, fields: dict) -> str:
        """Implement your custom formatting logic."""
        # Your formatting implementation
        return f"TITLE: {fields.get('title')}\nYEAR: {fields.get('year')}\n"

# Register custom writer  
editor = NFOEditor()
editor.register_writer('custom', CustomNFOWriter())
```

## 🔍 Error Handling

NFO Editor provides specific exception types for different error conditions:

```python
from nfo_editor import (
    NFOError,           # Base exception
    NFOParseError,      # Parsing failures
    NFOFieldError,      # Field operation errors
    NFOAccessError,     # File access issues
    NFOFormatError,     # Format not supported
    NFOValidationError  # Data validation errors
)

try:
    # Load and process files
    results = edit_nfo_files(
        directories=['/media/movies'],
        field_updates={'title': 'New Title'},
        backup=True
    )
    
    # Check for partial failures
    if results['failed_edits'] > 0:
        print("Some files failed to process:")
        for error in results['errors']:
            print(f"  {error['file_path']}: {error['error']}")

except NFOAccessError as e:
    print(f"Access error: {e}")
    print("Check file permissions and paths")

except NFOParseError as e:
    print(f"Parse error: {e}")
    print("File may be corrupted or in unsupported format")

except NFOFieldError as e:
    print(f"Field error: {e}")
    print("Check field names and value types")

except NFOError as e:
    print(f"General NFO error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🎯 Practical Examples

### 1. Media Library Cleanup Script
```python
import os
from nfo_editor import scan_nfo_files, edit_nfo_files, detect_nfo_format

def cleanup_media_library(base_path):
    """Clean up and standardize media library NFO files."""
    
    # Find all NFO files
    scan_results = scan_nfo_files(
        directories=[base_path],
        pattern='*.nfo',
        recursive=True
    )
    
    print(f"Found {len(scan_results['nfo_files'])} NFO files")
    
    # Standardize metadata
    edit_results = edit_nfo_files(
        directories=[base_path],
        field_updates={
            'updated': '2024-01-15T12:00:00Z',
            'library_version': '2.0',
            'processed_by': 'cleanup_script'
        },
        backup=True,
        max_files=100  # Process in batches
    )
    
    print(f"Updated {edit_results['successful_edits']} files")
    return edit_results

# Usage
results = cleanup_media_library('/media/movies')
```

### 2. Format Analysis Tool
```python
from collections import defaultdict
from nfo_editor import scan_nfo_files, detect_nfo_format

def analyze_nfo_formats(directories):
    """Analyze NFO file formats in directories."""
    
    # Find all potential NFO files
    scan_results = scan_nfo_files(
        directories=directories,
        pattern='*',  # All files
        recursive=True
    )
    
    format_stats = defaultdict(int)
    confidence_stats = defaultdict(list)
    
    for file_path in scan_results['nfo_files']:
        # Check if it's actually an NFO file
        format_info = detect_nfo_format(file_path)
        
        if format_info['confidence'] > 0.7:  # High confidence
            format_type = format_info['format']
            format_stats[format_type] += 1
            confidence_stats[format_type].append(format_info['confidence'])
    
    # Report results
    print("NFO Format Analysis:")
    for format_type, count in format_stats.items():
        avg_confidence = sum(confidence_stats[format_type]) / len(confidence_stats[format_type])
        print(f"  {format_type.upper()}: {count} files (avg confidence: {avg_confidence:.1%})")
    
    return format_stats

# Usage
stats = analyze_nfo_formats(['/media/movies', '/media/tv'])
```

### 3. Batch Format Converter
```python
import os
from nfo_editor import edit_nfo_files, detect_nfo_format

def convert_to_xml(source_dir, target_format='xml'):
    """Convert all NFO files to XML format."""
    
    print(f"Converting NFO files in {source_dir} to {target_format}")
    
    # Convert with backup
    results = edit_nfo_files(
        directories=[source_dir],
        field_updates={
            'converted_date': '2024-01-15T12:00:00Z',
            'converted_to': target_format,
            'original_format': 'preserved'
        },
        output_format=target_format,
        backup=True,
        max_files=50  # Process in batches
    )
    
    print(f"Conversion complete:")
    print(f"  Successfully converted: {results['successful_edits']}")
    print(f"  Failed conversions: {results['failed_edits']}")
    
    if results['errors']:
        print("Errors:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  {error['file_path']}: {error['error']}")
    
    return results

# Usage
convert_to_xml('/media/old-nfos')
```

### 4. Content Validation Tool
```python
from nfo_editor import load_nfo_file, scan_nfo_files

def validate_nfo_content(directories, required_fields=None):
    """Validate NFO files have required fields."""
    
    if required_fields is None:
        required_fields = ['title', 'year']
    
    # Find all NFO files
    scan_results = scan_nfo_files(directories, recursive=True)
    
    validation_results = {
        'valid_files': [],
        'invalid_files': [],
        'missing_fields': defaultdict(list)
    }
    
    for file_path in scan_results['nfo_files']:
        try:
            # Load file
            data = load_nfo_file(file_path)
            fields = data['fields']
            
            # Check required fields
            missing = []
            for field in required_fields:
                if field not in fields or not fields[field]:
                    missing.append(field)
            
            if missing:
                validation_results['invalid_files'].append(file_path)
                validation_results['missing_fields'][file_path] = missing
            else:
                validation_results['valid_files'].append(file_path)
                
        except Exception as e:
            validation_results['invalid_files'].append(file_path)
            validation_results['missing_fields'][file_path] = [f"Parse error: {e}"]
    
    # Report
    total_files = len(scan_results['nfo_files'])
    valid_count = len(validation_results['valid_files'])
    
    print(f"Validation Results:")
    print(f"  Total files: {total_files}")
    print(f"  Valid files: {valid_count} ({valid_count/total_files:.1%})")
    print(f"  Invalid files: {total_files - valid_count}")
    
    return validation_results

# Usage
results = validate_nfo_content(
    directories=['/media/movies'],
    required_fields=['title', 'year', 'genre']
)
```

## 🔧 Integration Examples

### Flask Web Application
```python
from flask import Flask, request, jsonify
from nfo_editor import scan_nfo_files, edit_nfo_files, load_nfo_file

app = Flask(__name__)

@app.route('/api/scan', methods=['POST'])
def scan_directories():
    """API endpoint to scan directories for NFO files."""
    data = request.json
    directories = data.get('directories', [])
    
    try:
        results = scan_nfo_files(directories, recursive=True)
        return jsonify({
            'success': True,
            'files_found': len(results['nfo_files']),
            'files': results['nfo_files'][:100]  # Limit response
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/edit', methods=['POST'])  
def edit_files():
    """API endpoint to edit NFO files."""
    data = request.json
    
    try:
        results = edit_nfo_files(
            directories=data['directories'],
            field_updates=data['field_updates'],
            backup=data.get('backup', True),
            dry_run=data.get('dry_run', False)
        )
        return jsonify({
            'success': True,
            'edited': results['successful_edits'],
            'failed': results['failed_edits']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Celery Task Queue
```python
from celery import Celery
from nfo_editor import edit_nfo_files

app = Celery('nfo_processor')

@app.task
def process_nfo_files(directories, field_updates, backup=True):
    """Asynchronous NFO file processing task."""
    
    try:
        results = edit_nfo_files(
            directories=directories,
            field_updates=field_updates,
            backup=backup,
            max_files=100  # Process in chunks
        )
        
        return {
            'success': True,
            'processed': results['successful_edits'],
            'failed': results['failed_edits'],
            'execution_time': results['execution_time_seconds']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Usage
result = process_nfo_files.delay(
    directories=['/media/movies'],
    field_updates={'updated': '2024-01-15'}
)
```

## 🚀 Performance Tips

### 1. Batch Processing
```python
# Process files in chunks for better memory usage
import os
from nfo_editor import edit_nfo_files

def process_large_collection(base_dir, chunk_size=100):
    """Process large collections in chunks."""
    
    # Get all subdirectories
    subdirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) 
               if os.path.isdir(os.path.join(base_dir, d))]
    
    total_processed = 0
    
    for subdir in subdirs:
        results = edit_nfo_files(
            directories=[subdir],
            field_updates={'processed_date': '2024-01-15'},
            backup=True,
            max_files=chunk_size
        )
        total_processed += results['successful_edits']
        print(f"Processed {subdir}: {results['successful_edits']} files")
    
    return total_processed
```

### 2. Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from nfo_editor import edit_nfo_files

def process_directory_parallel(directories, field_updates, max_workers=4):
    """Process multiple directories in parallel."""
    
    def process_single_dir(directory):
        return edit_nfo_files(
            directories=[directory],
            field_updates=field_updates,
            backup=True,
            max_files=50
        )
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_dir, dir) for dir in directories]
        
        for future in futures:
            result = future.result()
            results.append(result)
    
    # Combine results
    total_success = sum(r['successful_edits'] for r in results)
    total_failed = sum(r['failed_edits'] for r in results)
    
    return {
        'total_successful': total_success,
        'total_failed': total_failed,
        'directory_results': results
    }
```

### 3. Caching
```python
from functools import lru_cache
from nfo_editor import load_nfo_file

@lru_cache(maxsize=1000)
def cached_load_nfo(file_path):
    """Cache NFO file loading for repeated access."""
    return load_nfo_file(file_path)

# Usage - subsequent calls with same file_path return cached data
data1 = cached_load_nfo('/media/movie.nfo')  # Loads from disk
data2 = cached_load_nfo('/media/movie.nfo')  # Returns cached data
```

## 🔗 Next Steps

- **[⚡ CLI Commands](cli-commands.md)** - Command-line interface
- **[📋 Configuration Guide](configuration.md)** - YAML configuration system
- **[🧩 Extending NFO Editor](extending.md)** - Creating custom parsers and writers
- **[🧪 Development Guide](development.md)** - Contributing to the project

---

The Python API provides the full power of NFO Editor for integration into your own applications and automation workflows!
