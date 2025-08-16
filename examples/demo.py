#!/usr/bin/env python3
"""
Demo script showing NFO Editor library functionality.

This script demonstrates the key features of the NFO Editor library
including scanning, format detection, parsing, and editing NFO files.

Author: NFO Editor Team
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import nfo_editor
sys.path.insert(0, str(Path(__file__).parent.parent))

from nfo_editor import (
    edit_nfo_files, scan_nfo_files, detect_nfo_format, load_nfo_file,
    NFOEditor, NFOScanner, NFOFormatDetector
)


def demo_scanning():
    """Demonstrate directory scanning functionality."""
    print("🔍 Demo: Scanning for NFO files")
    print("=" * 50)
    
    # Get the examples directory
    examples_dir = Path(__file__).parent
    
    # Scan for NFO files
    result = scan_nfo_files(examples_dir)
    
    print(f"Found {len(result['nfo_files'])} NFO files:")
    for file_path in result['nfo_files']:
        print(f"  📄 {file_path}")
    
    print(f"Scan completed in {result['scan_time_seconds']:.3f} seconds")
    print()


def demo_format_detection():
    """Demonstrate format detection functionality."""
    print("🔍 Demo: Format Detection")
    print("=" * 50)
    
    examples_dir = Path(__file__).parent
    nfo_files = list(examples_dir.glob("*.nfo")) + list(examples_dir.glob("*.xml")) + list(examples_dir.glob("*.json"))
    
    for file_path in nfo_files:
        result = detect_nfo_format(file_path)
        print(f"📄 {file_path.name}")
        print(f"   Format: {result['format']} (confidence: {result['confidence']:.2f})")
        print(f"   Encoding: {result['encoding']}")
        print()


def demo_loading_files():
    """Demonstrate loading and parsing NFO files."""
    print("📖 Demo: Loading NFO Files")
    print("=" * 50)
    
    examples_dir = Path(__file__).parent
    
    # Load different format files
    files_to_load = ['movie.xml', 'movie.json', 'movie.nfo', 'show.nfo']
    
    for filename in files_to_load:
        file_path = examples_dir / filename
        if file_path.exists():
            print(f"📄 Loading {filename}...")
            result = load_nfo_file(file_path)
            
            print(f"   Format: {result['format_type']}")
            print(f"   Fields found: {len(result['fields'])}")
            
            # Show some key fields
            flat_fields = result['all_fields_flat']
            for field_name in ['title', 'year', 'genre', 'rating']:
                # Try to find field with case-insensitive search
                field_value = None
                for key, value in flat_fields.items():
                    if field_name.lower() in key.lower():
                        field_value = value
                        break
                
                if field_value is not None:
                    print(f"   {field_name.capitalize()}: {field_value}")
            
            print()


def demo_editing():
    """Demonstrate editing NFO files."""
    print("✏️  Demo: Editing NFO Files")
    print("=" * 50)
    
    examples_dir = Path(__file__).parent
    
    # Create a temporary copy for editing
    import shutil
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Copy example files to temp directory
        for source_file in examples_dir.glob("movie.*"):
            shutil.copy2(source_file, temp_dir / source_file.name)
        
        print("📋 Preview of changes (dry run):")
        preview_result = edit_nfo_files(
            directories=[temp_dir],
            field_updates={
                'rating': '9.5',
                'genre': 'Sci-Fi/Action',
                'studio': 'Updated Studio'
            },
            dry_run=True
        )
        
        for file_preview in preview_result['file_previews']:
            if 'error' not in file_preview:
                print(f"  📄 {Path(file_preview['file_path']).name} ({file_preview['format']})")
                for field, change in file_preview['field_changes'].items():
                    if change['will_change']:
                        print(f"    {field}: {change['current']} → {change['new']}")
        
        print("\n💾 Applying changes...")
        edit_result = edit_nfo_files(
            directories=[temp_dir],
            field_updates={
                'rating': '9.5',
                'genre': 'Sci-Fi/Action'
            },
            backup=True
        )
        
        print(f"✅ Successfully edited {edit_result['successful_edits']} files")
        print(f"❌ Failed to edit {edit_result['failed_edits']} files")
        print(f"⏱️  Execution time: {edit_result['execution_time_seconds']:.3f} seconds")


def demo_advanced_usage():
    """Demonstrate advanced usage with NFOEditor class."""
    print("🚀 Demo: Advanced Usage")
    print("=" * 50)
    
    examples_dir = Path(__file__).parent
    
    # Create an editor instance
    editor = NFOEditor(
        directories=[examples_dir],
        create_backups=False,
        preserve_format=True
    )
    
    # Get statistics
    stats = editor.get_statistics()
    print("📊 Editor Statistics:")
    print(f"   Directories configured: {stats['directories_configured']}")
    print(f"   NFO files found: {stats.get('scan_statistics', {}).get('nfo_files_found', 'N/A')}")
    print(f"   Parsers available: {', '.join(stats['parsers_available'])}")
    print(f"   Writers available: {', '.join(stats['writers_available'])}")
    
    # Load a specific file
    movie_xml = examples_dir / 'movie.xml'
    if movie_xml.exists():
        print(f"\n📖 Loading {movie_xml.name} with advanced features...")
        nfo_data = editor.load_file(movie_xml)
        
        print(f"   Original format: {nfo_data.format_type}")
        print(f"   File encoding: {nfo_data.encoding}")
        print(f"   Total fields: {len(nfo_data.get_all_fields())}")
        
        # Show metadata
        if nfo_data.metadata:
            print(f"   XML elements: {nfo_data.metadata.get('element_count', 'N/A')}")
            print(f"   Root element: {nfo_data.metadata.get('root_element', 'N/A')}")


def main():
    """Run all demos."""
    print("🎬 NFO Editor Library Demo")
    print("=" * 50)
    print("This demo showcases the key features of the NFO Editor library.")
    print("Make sure you're running this from the examples directory.\n")
    
    try:
        demo_scanning()
        demo_format_detection()
        demo_loading_files()
        demo_editing()
        demo_advanced_usage()
        
        print("🎉 Demo completed successfully!")
        print("\nTry the CLI interface:")
        print("  nfo-editor scan examples/")
        print("  nfo-editor detect examples/movie.xml")
        print("  nfo-editor edit examples/ --set rating=9.0 --dry-run")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
