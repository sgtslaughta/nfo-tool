#!/usr/bin/env python3
"""
Basic tests for NFO Editor library functionality.

This module contains basic tests to verify that the core functionality
of the NFO Editor library is working correctly.

Author: NFO Editor Team
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nfo_editor import (
    NFOEditor, NFOScanner, NFOFormatDetector, NFOData,
    edit_nfo_files, scan_nfo_files, detect_nfo_format, load_nfo_file,
    NFOError, NFOParseError, NFOFieldError, NFOAccessError, NFOFormatError
)
from nfo_editor.parsers.xml_parser import XMLNFOParser
from nfo_editor.parsers.json_parser import JSONNFOParser
from nfo_editor.parsers.text_parser import TextNFOParser
from nfo_editor.writers.xml_writer import XMLNFOWriter
from nfo_editor.writers.json_writer import JSONNFOWriter
from nfo_editor.writers.text_writer import TextNFOWriter


class TestNFOData(unittest.TestCase):
    """Test NFOData class functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = {
            'title': 'Test Movie',
            'year': 2024,
            'genre': 'Action',
            'nested': {
                'field1': 'value1',
                'field2': 'value2'
            }
        }
        self.nfo_data = NFOData(
            file_path=Path('/test/movie.nfo'),
            format_type='test',
            data=self.sample_data
        )
    
    def test_get_field(self):
        """Test getting field values."""
        self.assertEqual(self.nfo_data.get_field('title'), 'Test Movie')
        self.assertEqual(self.nfo_data.get_field('year'), 2024)
        self.assertEqual(self.nfo_data.get_field('nested.field1'), 'value1')
        self.assertEqual(self.nfo_data.get_field('nonexistent'), None)
        self.assertEqual(self.nfo_data.get_field('nonexistent', 'default'), 'default')
    
    def test_set_field(self):
        """Test setting field values."""
        self.nfo_data.set_field('title', 'New Title')
        self.assertEqual(self.nfo_data.get_field('title'), 'New Title')
        
        self.nfo_data.set_field('new_field', 'New Value')
        self.assertEqual(self.nfo_data.get_field('new_field'), 'New Value')
        
        self.nfo_data.set_field('nested.new_field', 'Nested Value')
        self.assertEqual(self.nfo_data.get_field('nested.new_field'), 'Nested Value')
    
    def test_has_field(self):
        """Test checking field existence."""
        self.assertTrue(self.nfo_data.has_field('title'))
        self.assertTrue(self.nfo_data.has_field('nested.field1'))
        self.assertFalse(self.nfo_data.has_field('nonexistent'))
    
    def test_delete_field(self):
        """Test deleting fields."""
        self.assertTrue(self.nfo_data.delete_field('genre'))
        self.assertFalse(self.nfo_data.has_field('genre'))
        
        self.assertTrue(self.nfo_data.delete_field('nested.field1'))
        self.assertFalse(self.nfo_data.has_field('nested.field1'))
        
        self.assertFalse(self.nfo_data.delete_field('nonexistent'))
    
    def test_get_all_fields(self):
        """Test getting all fields as flat dictionary."""
        all_fields = self.nfo_data.get_all_fields()
        
        self.assertIn('title', all_fields)
        self.assertIn('nested.field1', all_fields)
        self.assertIn('nested.field2', all_fields)
        self.assertEqual(all_fields['title'], 'Test Movie')
        self.assertEqual(all_fields['nested.field1'], 'value1')


class TestParsers(unittest.TestCase):
    """Test NFO parser functionality."""
    
    def test_xml_parser(self):
        """Test XML parser with sample data."""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<movie>
    <title>Test Movie</title>
    <year>2024</year>
    <genre>Action</genre>
    <rating>8.5</rating>
</movie>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            f.flush()
            
            parser = XMLNFOParser()
            self.assertTrue(parser.can_parse(f.name))
            
            nfo_data = parser.parse(f.name)
            self.assertEqual(nfo_data.format_type, 'xml')
            self.assertEqual(nfo_data.get_field('title'), 'Test Movie')
            self.assertEqual(nfo_data.get_field('year'), 2024)
            
            Path(f.name).unlink()  # Clean up
    
    def test_json_parser(self):
        """Test JSON parser with sample data."""
        json_data = {
            'title': 'Test Movie',
            'year': 2024,
            'genre': 'Action',
            'rating': 8.5
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            f.flush()
            
            parser = JSONNFOParser()
            self.assertTrue(parser.can_parse(f.name))
            
            nfo_data = parser.parse(f.name)
            self.assertEqual(nfo_data.format_type, 'json')
            self.assertEqual(nfo_data.get_field('title'), 'Test Movie')
            self.assertEqual(nfo_data.get_field('year'), 2024)
            
            Path(f.name).unlink()  # Clean up
    
    def test_text_parser(self):
        """Test text parser with sample data."""
        text_content = '''Title: Test Movie
Year: 2024
Genre: Action
Rating: 8.5
Plot: A test movie for demonstrating the NFO editor library.'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nfo', delete=False) as f:
            f.write(text_content)
            f.flush()
            
            parser = TextNFOParser()
            self.assertTrue(parser.can_parse(f.name))
            
            nfo_data = parser.parse(f.name)
            self.assertEqual(nfo_data.format_type, 'text')
            self.assertEqual(nfo_data.get_field('title'), 'Test Movie')
            self.assertEqual(nfo_data.get_field('year'), '2024')  # Text parser keeps as string
            
            Path(f.name).unlink()  # Clean up


class TestFormatDetection(unittest.TestCase):
    """Test format detection functionality."""
    
    def test_xml_detection(self):
        """Test XML format detection."""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<movie>
    <title>Test Movie</title>
</movie>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            f.flush()
            
            detector = NFOFormatDetector()
            result = detector.detect_format(f.name)
            
            self.assertEqual(result.format_type.value, 'xml')
            self.assertGreater(result.confidence, 0.7)
            
            Path(f.name).unlink()  # Clean up
    
    def test_json_detection(self):
        """Test JSON format detection."""
        json_content = '''{"title": "Test Movie", "year": 2024}'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            f.flush()
            
            detector = NFOFormatDetector()
            result = detector.detect_format(f.name)
            
            self.assertEqual(result.format_type.value, 'json')
            self.assertGreater(result.confidence, 0.7)
            
            Path(f.name).unlink()  # Clean up


class TestScanning(unittest.TestCase):
    """Test directory scanning functionality."""
    
    def test_scanner_basic(self):
        """Test basic scanning functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # Create test NFO files
            (temp_dir / 'movie1.nfo').write_text('Title: Movie 1')
            (temp_dir / 'movie2.xml').write_text('<movie><title>Movie 2</title></movie>')
            (temp_dir / 'movie3.json').write_text('{"title": "Movie 3"}')
            
            scanner = NFOScanner()
            result = scanner.scan_directories([temp_dir])
            
            self.assertEqual(len(result.nfo_files), 3)
            self.assertGreater(result.total_files_scanned, 0)
            self.assertEqual(result.directories_scanned, 1)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_scan_nfo_files(self):
        """Test scan_nfo_files convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # Create test files
            (temp_dir / 'test.nfo').write_text('Title: Test')
            (temp_dir / 'test.xml').write_text('<movie><title>Test</title></movie>')
            
            result = scan_nfo_files([temp_dir])
            
            self.assertIn('nfo_files', result)
            self.assertIn('total_files_scanned', result)
            self.assertEqual(len(result['nfo_files']), 2)
    
    def test_detect_nfo_format(self):
        """Test detect_nfo_format convenience function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<movie><title>Test</title></movie>')
            f.flush()
            
            result = detect_nfo_format(f.name)
            
            self.assertIn('format', result)
            self.assertIn('confidence', result)
            self.assertEqual(result['format'], 'xml')
            
            Path(f.name).unlink()  # Clean up
    
    def test_load_nfo_file(self):
        """Test load_nfo_file convenience function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'title': 'Test Movie', 'year': 2024}, f)
            f.flush()
            
            result = load_nfo_file(f.name)
            
            self.assertIn('fields', result)
            self.assertIn('format_type', result)
            self.assertEqual(result['format_type'], 'json')
            self.assertEqual(result['fields']['title'], 'Test Movie')
            
            Path(f.name).unlink()  # Clean up


if __name__ == '__main__':
    print("Running NFO Editor Library Tests...")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)
