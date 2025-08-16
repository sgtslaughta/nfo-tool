"""
Syntax Highlighting for NFO Content

Advanced syntax highlighting with Rich formatting for NFO files,
supporting multiple formats with customizable themes and line numbers.

Author: NFO Editor Team
"""

from typing import Optional, Union, Dict, Any
from rich.syntax import Syntax
from rich.console import Console, ConsoleRenderable
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re


class NFOSyntaxHighlighter:
    """
    Advanced syntax highlighter for NFO content with format detection
    and customizable display options.
    """
    
    # Theme mappings for different content types
    THEME_MAP = {
        'xml': 'monokai',
        'json': 'github-dark', 
        'yaml': 'native',
        'text': 'github-dark',
        'unknown': 'default'
    }
    
    def __init__(self, 
                 console: Optional[Console] = None,
                 default_theme: str = "auto",
                 show_line_numbers: bool = True,
                 word_wrap: bool = False,
                 max_content_length: int = 2000):
        """
        Initialize syntax highlighter.
        
        Args:
            console: Rich Console instance
            default_theme: Default theme for highlighting
            show_line_numbers: Whether to show line numbers
            word_wrap: Whether to wrap long lines
            max_content_length: Maximum content length to highlight
        """
        self.console = console or Console()
        self.default_theme = default_theme
        self.show_line_numbers = show_line_numbers
        self.word_wrap = word_wrap
        self.max_content_length = max_content_length
    
    def highlight_content(self, 
                         content: str,
                         content_type: str = "auto",
                         title: Optional[str] = None,
                         theme: Optional[str] = None,
                         show_panel: bool = True) -> ConsoleRenderable:
        """
        Highlight content with automatic format detection.
        
        Args:
            content: Content to highlight
            content_type: Content type ('xml', 'json', 'yaml', 'text', 'auto')
            title: Optional title for panel display
            theme: Optional theme override
            show_panel: Whether to wrap in a Rich panel
            
        Returns:
            Rich renderable object (Syntax or Panel)
        """
        # Auto-detect content type if requested
        if content_type == "auto":
            content_type = self.detect_content_type(content)
        
        # Truncate content if too long
        if len(content) > self.max_content_length:
            content = content[:self.max_content_length] + "\n... [content truncated]"
        
        # Choose appropriate theme
        effective_theme = theme or self._get_theme_for_content(content_type)
        
        # Create syntax object
        try:
            syntax = Syntax(
                content,
                lexer=self._get_lexer_for_content(content_type),
                theme=effective_theme,
                line_numbers=self.show_line_numbers,
                word_wrap=self.word_wrap,
                background_color="default"
            )
        except Exception:
            # Fallback to plain text if syntax highlighting fails
            syntax = Syntax(
                content,
                lexer="text",
                theme="default",
                line_numbers=self.show_line_numbers,
                word_wrap=self.word_wrap
            )
        
        # Wrap in panel if requested
        if show_panel:
            panel_title = title or f"📄 {content_type.upper()} Content"
            return Panel(
                syntax,
                title=panel_title,
                border_style="dim",
                expand=False
            )
        
        return syntax
    
    def detect_content_type(self, content: str) -> str:
        """
        Auto-detect content type based on content analysis.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected content type
        """
        content = content.strip()
        
        if not content:
            return "text"
        
        # XML detection
        if content.startswith('<?xml') or (content.startswith('<') and content.endswith('>')):
            try:
                ET.fromstring(content)
                return "xml"
            except ET.ParseError:
                pass
        
        # JSON detection
        if (content.startswith('{') and content.endswith('}')) or \
           (content.startswith('[') and content.endswith(']')):
            try:
                json.loads(content)
                return "json"
            except json.JSONDecodeError:
                pass
        
        # YAML detection (basic heuristics)
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*:\s*', content, re.MULTILINE):
            return "yaml"
        
        # Default to text
        return "text"
    
    def _get_theme_for_content(self, content_type: str) -> str:
        """Get appropriate theme for content type."""
        if self.default_theme != "auto":
            return self.default_theme
        
        return self.THEME_MAP.get(content_type, self.THEME_MAP['unknown'])
    
    def _get_lexer_for_content(self, content_type: str) -> str:
        """Get appropriate lexer for content type."""
        lexer_map = {
            'xml': 'xml',
            'json': 'json',
            'yaml': 'yaml',
            'text': 'text'
        }
        return lexer_map.get(content_type, 'text')


# Global highlighter instance
_highlighter: Optional[NFOSyntaxHighlighter] = None


def get_highlighter() -> NFOSyntaxHighlighter:
    """Get or create global syntax highlighter instance."""
    global _highlighter
    if _highlighter is None:
        _highlighter = NFOSyntaxHighlighter()
    return _highlighter


def format_nfo_content(content: str, 
                      format_type: str = "auto",
                      title: Optional[str] = None,
                      theme: Optional[str] = None,
                      show_panel: bool = True) -> ConsoleRenderable:
    """
    Format NFO content with syntax highlighting.
    
    Args:
        content: NFO content to format
        format_type: Content format ('xml', 'json', 'yaml', 'text', 'auto')
        title: Optional title for display
        theme: Optional theme override
        show_panel: Whether to wrap in panel
        
    Returns:
        Rich renderable object with syntax highlighting
    """
    highlighter = get_highlighter()
    return highlighter.highlight_content(
        content=content,
        content_type=format_type,
        title=title,
        theme=theme,
        show_panel=show_panel
    )


def highlight_json(json_str: str, 
                  title: str = "JSON Content",
                  pretty_print: bool = True,
                  theme: Optional[str] = None) -> ConsoleRenderable:
    """
    Highlight JSON content with optional pretty printing.
    
    Args:
        json_str: JSON string to highlight
        title: Title for the display panel
        pretty_print: Whether to format JSON for readability
        theme: Optional theme override
        
    Returns:
        Rich renderable with JSON syntax highlighting
    """
    # Pretty print if requested and valid JSON
    if pretty_print:
        try:
            parsed = json.loads(json_str)
            json_str = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pass  # Use original string if parsing fails
    
    highlighter = get_highlighter()
    return highlighter.highlight_content(
        content=json_str,
        content_type="json",
        title=title,
        theme=theme
    )


def highlight_xml(xml_str: str,
                 title: str = "XML Content", 
                 pretty_print: bool = True,
                 theme: Optional[str] = None) -> ConsoleRenderable:
    """
    Highlight XML content with optional pretty printing.
    
    Args:
        xml_str: XML string to highlight
        title: Title for the display panel
        pretty_print: Whether to format XML for readability
        theme: Optional theme override
        
    Returns:
        Rich renderable with XML syntax highlighting
    """
    # Pretty print if requested and valid XML
    if pretty_print:
        try:
            parsed = xml.dom.minidom.parseString(xml_str)
            xml_str = parsed.toprettyxml(indent="  ", encoding=None)
            # Remove extra whitespace lines
            xml_str = re.sub(r'\n\s*\n', '\n', xml_str)
            xml_str = xml_str.strip()
        except Exception:
            pass  # Use original string if parsing fails
    
    highlighter = get_highlighter()
    return highlighter.highlight_content(
        content=xml_str,
        content_type="xml",
        title=title,
        theme=theme
    )


def highlight_yaml(yaml_str: str,
                  title: str = "YAML Content",
                  theme: Optional[str] = None) -> ConsoleRenderable:
    """
    Highlight YAML content.
    
    Args:
        yaml_str: YAML string to highlight
        title: Title for the display panel
        theme: Optional theme override
        
    Returns:
        Rich renderable with YAML syntax highlighting
    """
    highlighter = get_highlighter()
    return highlighter.highlight_content(
        content=yaml_str,
        content_type="yaml",
        title=title,
        theme=theme
    )


def create_diff_display(before_content: str,
                       after_content: str,
                       content_type: str = "auto",
                       title: str = "Content Diff") -> Table:
    """
    Create a side-by-side diff display with syntax highlighting.
    
    Args:
        before_content: Original content
        after_content: Modified content
        content_type: Content type for highlighting
        title: Title for the diff table
        
    Returns:
        Rich Table with side-by-side diff
    """
    table = Table(title=title)
    table.add_column("Before", style="dim", ratio=1)
    table.add_column("After", style="white", ratio=1)
    
    highlighter = get_highlighter()
    
    # Create highlighted versions (without panels)
    before_highlighted = highlighter.highlight_content(
        before_content, content_type, show_panel=False
    )
    after_highlighted = highlighter.highlight_content(
        after_content, content_type, show_panel=False
    )
    
    table.add_row(before_highlighted, after_highlighted)
    
    return table


def create_field_comparison_table(before_fields: Dict[str, Any],
                                after_fields: Dict[str, Any],
                                title: str = "Field Changes") -> Table:
    """
    Create a table showing field-by-field changes.
    
    Args:
        before_fields: Original field values
        after_fields: Modified field values  
        title: Title for the comparison table
        
    Returns:
        Rich Table with field comparisons
    """
    table = Table(title=title)
    table.add_column("Field", style="cyan")
    table.add_column("Before", style="dim")
    table.add_column("After", style="white")
    table.add_column("Status", style="bold")
    
    all_fields = set(before_fields.keys()) | set(after_fields.keys())
    
    for field in sorted(all_fields):
        before_val = before_fields.get(field, "[dim]Not set[/dim]")
        after_val = after_fields.get(field, "[dim]Not set[/dim]")
        
        # Format values for display
        before_str = _format_value_for_table(before_val)
        after_str = _format_value_for_table(after_val)
        
        # Determine status
        if before_val != after_val:
            if field not in before_fields:
                status = "[green]✅ Added[/green]"
            elif field not in after_fields:
                status = "[red]❌ Removed[/red]"
            else:
                status = "[yellow]🔄 Changed[/yellow]"
        else:
            status = "[dim]➖ Same[/dim]"
        
        table.add_row(field, before_str, after_str, status)
    
    return table


def _format_value_for_table(value: Any) -> str:
    """Format a value for display in comparison tables."""
    if value is None:
        return "[dim]None[/dim]"
    elif isinstance(value, bool):
        return "✅ True" if value else "❌ False"
    elif isinstance(value, (list, tuple)):
        if len(value) == 0:
            return "[dim]Empty list[/dim]"
        elif len(value) == 1:
            return f"[{_format_value_for_table(value[0])}]"
        else:
            return f"[{len(value)} items]"
    elif isinstance(value, dict):
        return f"{{dict with {len(value)} keys}}"
    elif isinstance(value, str):
        if len(value) > 50:
            return value[:47] + "..."
        return value
    else:
        return str(value)
