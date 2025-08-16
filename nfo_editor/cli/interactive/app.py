"""
Interactive TUI Application (Placeholder)

This module will contain the main Textual application for interactive mode.
Currently a placeholder that will be implemented in Phase 4.

Author: NFO Editor Team
"""

from typing import Optional


class NFOEditorApp:
    """
    Main interactive TUI application.
    
    This is a placeholder implementation. The full interactive mode
    will be implemented in Phase 4 of the modernization plan.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the interactive application.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    def run(self):
        """
        Run the interactive application.
        
        Currently shows a placeholder message.
        """
        print("🚧 Interactive Mode Coming Soon!")
        print()
        print("Interactive TUI mode will be implemented in Phase 4.")
        print("For now, please use the enhanced CLI commands:")
        print()
        print("  nfo-editor --scan /media/movies")
        print("  nfo-editor --edit /media/tv --set genre=Drama")
        print("  nfo-editor --detect file.nfo")
        print("  nfo-editor --load file.nfo")
        print()
        print("Use --help for full command reference.")
