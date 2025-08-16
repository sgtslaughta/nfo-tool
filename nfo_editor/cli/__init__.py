"""
NFO Editor CLI Package

This package provides the modern Click-based command-line interface for NFO Editor,
featuring interactive TUI mode as default, enhanced CLI arguments, and YAML configuration support.

Key Features:
- Interactive TUI mode (default behavior)
- Rich-enhanced CLI commands  
- YAML configuration profiles
- Beautiful terminal output with progress tracking

Author: NFO Editor Team
"""

from .main import cli

__all__ = ["cli"]
