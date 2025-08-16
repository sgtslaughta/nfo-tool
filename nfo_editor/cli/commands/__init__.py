"""
CLI Commands Package

Contains Click command implementations for direct CLI usage.
These commands are triggered by flags like --scan, --edit, --detect, --load.

Author: NFO Editor Team
"""

from .scan import scan_command
from .edit import edit_command  
from .detect import detect_command
from .load import load_command

__all__ = [
    "scan_command",
    "edit_command", 
    "detect_command",
    "load_command"
]
