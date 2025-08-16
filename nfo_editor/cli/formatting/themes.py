"""
Rich Themes Management

This module handles Rich color themes and styling for consistent, beautiful output
across all CLI commands and interactive modes.

Author: NFO Editor Team
"""

from typing import List, Dict, Optional
from rich.console import Console
from rich.theme import Theme
from rich import get_console
import os

# Global theme storage
_current_theme = "auto"
_custom_themes: Dict[str, Theme] = {}

# Define custom theme configurations
THEME_CONFIGS = {
    "auto": {
        "info": "bright_blue",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "accent": "magenta", 
        "dim": "bright_black",
        "highlight": "cyan"
    },
    "dark": {
        "info": "bright_blue",
        "warning": "bright_yellow", 
        "error": "bright_red",
        "success": "bright_green",
        "accent": "bright_magenta",
        "dim": "bright_black",
        "highlight": "bright_cyan"
    },
    "light": {
        "info": "blue",
        "warning": "yellow3",
        "error": "red3", 
        "success": "green3",
        "accent": "purple",
        "dim": "grey50",
        "highlight": "cyan3"
    },
    "monokai": {
        "info": "#66D9EF",      # Cyan
        "warning": "#E6DB74",   # Yellow
        "error": "#F92672",     # Pink/Red
        "success": "#A6E22E",   # Green
        "accent": "#AE81FF",    # Purple
        "dim": "#75715E",       # Grey
        "highlight": "#FD971F"  # Orange
    }
}


def get_theme(theme_name: str = "auto") -> str:
    """
    Get the specified Rich theme name.
    
    Args:
        theme_name: Name of the theme to get
        
    Returns:
        Current theme name
    """
    global _current_theme
    if theme_name in THEME_CONFIGS:
        return theme_name
    return _current_theme


def set_theme(theme_name: str = "auto") -> None:
    """
    Set the active Rich theme globally.
    
    Args:
        theme_name: Name of the theme to activate
    """
    global _current_theme
    
    if theme_name not in THEME_CONFIGS:
        theme_name = "auto"
    
    _current_theme = theme_name
    
    # Auto-detect based on terminal settings if auto theme
    if theme_name == "auto":
        theme_name = detect_terminal_theme()
    
    # Create and apply the Rich theme
    if theme_name in THEME_CONFIGS:
        rich_theme = Theme(THEME_CONFIGS[theme_name])
        
        # Apply to global console if available
        try:
            console = get_console()
            console.push_theme(rich_theme)
        except Exception:
            # Fallback: store for later application
            _custom_themes[theme_name] = rich_theme


def detect_terminal_theme() -> str:
    """
    Auto-detect the appropriate theme based on terminal settings.
    
    Returns:
        Detected theme name
    """
    # Check environment variables for theme hints
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        # VS Code integrated terminal - assume dark
        return 'dark'
    
    # Check for common dark terminal indicators
    term = os.environ.get('TERM', '').lower()
    colorterm = os.environ.get('COLORTERM', '').lower()
    
    if 'dark' in term or 'dark' in colorterm:
        return 'dark'
    elif 'light' in term or 'light' in colorterm:
        return 'light'
    
    # Default to dark theme for better compatibility
    return 'dark'


def available_themes() -> List[str]:
    """
    Get list of available theme names.
    
    Returns:
        List of available theme names
    """
    return list(THEME_CONFIGS.keys())


def get_current_theme() -> str:
    """
    Get the currently active theme name.
    
    Returns:
        Current theme name
    """
    global _current_theme
    return _current_theme


def create_themed_console(theme_name: Optional[str] = None) -> Console:
    """
    Create a Rich Console with the specified theme applied.
    
    Args:
        theme_name: Optional theme name, uses current theme if None
        
    Returns:
        Console instance with theme applied
    """
    if theme_name is None:
        theme_name = _current_theme
    
    if theme_name == "auto":
        theme_name = detect_terminal_theme()
    
    if theme_name in THEME_CONFIGS:
        rich_theme = Theme(THEME_CONFIGS[theme_name])
        return Console(theme=rich_theme)
    else:
        return Console()


def get_theme_colors(theme_name: Optional[str] = None) -> Dict[str, str]:
    """
    Get the color configuration for a theme.
    
    Args:
        theme_name: Optional theme name, uses current theme if None
        
    Returns:
        Dictionary of color names to color values
    """
    if theme_name is None:
        theme_name = _current_theme
        
    if theme_name == "auto":
        theme_name = detect_terminal_theme()
        
    return THEME_CONFIGS.get(theme_name, THEME_CONFIGS["auto"])
