"""
Rich Progress Trackers

Progress bar components for batch operations with real-time feedback,
error handling, and beautiful Rich formatting.

Author: NFO Editor Team
"""

from typing import Optional, List, Dict, Any, Callable, Union
from rich.progress import (
    Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, 
    TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn,
    DownloadColumn, TransferSpeedColumn
)
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from contextlib import contextmanager
import time
from dataclasses import dataclass, field
from enum import Enum


class OperationType(Enum):
    """Types of operations that can be tracked."""
    SCAN = "scan"
    EDIT = "edit"
    LOAD = "load"
    DETECT = "detect"
    BACKUP = "backup"


@dataclass
class OperationStats:
    """Statistics for tracking operations."""
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time


class BatchProgressTracker:
    """
    Advanced progress tracker for batch operations with Rich formatting.
    
    Provides real-time progress updates, error tracking, and statistics
    for operations across multiple files or directories.
    """
    
    def __init__(self, 
                 console: Optional[Console] = None,
                 operation_type: OperationType = OperationType.SCAN,
                 show_speed: bool = False,
                 show_eta: bool = True):
        """
        Initialize batch progress tracker.
        
        Args:
            console: Rich Console instance (creates new if None)
            operation_type: Type of operation being tracked
            show_speed: Whether to show processing speed
            show_eta: Whether to show estimated time remaining
        """
        self.console = console or Console()
        self.operation_type = operation_type
        self.show_speed = show_speed
        self.show_eta = show_eta
        
        self.stats = OperationStats()
        self.progress: Optional[Progress] = None
        self.main_task: Optional[TaskID] = None
        self.subtasks: Dict[str, TaskID] = {}
        
        # Configure progress columns based on operation type
        self._setup_progress_columns()
    
    def _setup_progress_columns(self):
        """Setup progress bar columns based on operation type and settings."""
        columns = [
            SpinnerColumn(spinner="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn()
        ]
        
        if self.show_eta:
            columns.append(TimeRemainingColumn())
        
        if self.show_speed:
            columns.extend([
                TextColumn("•"),
                TransferSpeedColumn()
            ])
        
        self.progress_columns = columns
    
    @contextmanager
    def track_operation(self, 
                       total_items: int, 
                       operation_description: str = None,
                       show_summary: bool = True):
        """
        Context manager for tracking a batch operation.
        
        Args:
            total_items: Total number of items to process
            operation_description: Description of the operation
            show_summary: Whether to show summary at completion
            
        Yields:
            BatchProgressTracker instance for updating progress
        """
        self.stats.total_items = total_items
        self.stats.start_time = time.time()
        
        if not operation_description:
            operation_description = f"{self.operation_type.value.title()}ing items..."
        
        try:
            with Progress(
                *self.progress_columns,
                console=self.console,
                refresh_per_second=4
            ) as progress:
                self.progress = progress
                self.main_task = progress.add_task(
                    f"[cyan]{operation_description}",
                    total=total_items
                )
                
                yield self
                
        finally:
            self.stats.end_time = time.time()
            if show_summary:
                self.show_completion_summary()
    
    def update_progress(self, 
                       completed: int = 1,
                       description: Optional[str] = None,
                       current_item: Optional[str] = None):
        """
        Update the main progress bar.
        
        Args:
            completed: Number of items completed (increment)
            description: Optional new description
            current_item: Current item being processed (for display)
        """
        if not self.progress or self.main_task is None:
            return
        
        self.stats.completed_items += completed
        
        # Update description with current item if provided
        if description:
            display_desc = f"[cyan]{description}"
            if current_item:
                display_desc += f" • [dim]{current_item}[/dim]"
        elif current_item:
            base_desc = f"{self.operation_type.value.title()}ing"
            display_desc = f"[cyan]{base_desc} • [dim]{current_item}[/dim]"
        else:
            display_desc = None
        
        self.progress.update(
            self.main_task,
            advance=completed,
            description=display_desc
        )
    
    def add_error(self, error_message: str, item_name: str = None):
        """
        Record an error during processing.
        
        Args:
            error_message: Description of the error
            item_name: Name of the item that caused the error
        """
        self.stats.failed_items += 1
        if item_name:
            full_error = f"{item_name}: {error_message}"
        else:
            full_error = error_message
        self.stats.errors.append(full_error)
    
    def skip_item(self, reason: str = None, item_name: str = None):
        """
        Record a skipped item.
        
        Args:
            reason: Reason for skipping
            item_name: Name of the skipped item
        """
        self.stats.skipped_items += 1
        if reason and item_name:
            self.stats.errors.append(f"Skipped {item_name}: {reason}")
    
    def create_subtask(self, 
                      task_id: str, 
                      description: str, 
                      total: int) -> Optional[TaskID]:
        """
        Create a subtask for tracking sub-operations.
        
        Args:
            task_id: Unique identifier for the subtask
            description: Description of the subtask
            total: Total items for this subtask
            
        Returns:
            TaskID for the created subtask
        """
        if not self.progress:
            return None
        
        subtask = self.progress.add_task(
            f"[yellow]{description}",
            total=total
        )
        self.subtasks[task_id] = subtask
        return subtask
    
    def update_subtask(self, 
                      task_id: str, 
                      advance: int = 1, 
                      description: Optional[str] = None):
        """
        Update a subtask progress.
        
        Args:
            task_id: ID of the subtask to update
            advance: Progress to advance
            description: Optional new description
        """
        if not self.progress or task_id not in self.subtasks:
            return
        
        task_kwargs = {'advance': advance}
        if description:
            task_kwargs['description'] = f"[yellow]{description}"
        
        self.progress.update(self.subtasks[task_id], **task_kwargs)
    
    def show_completion_summary(self):
        """Display operation completion summary."""
        # Create summary statistics table
        summary_table = Table(title=f"📊 {self.operation_type.value.title()} Summary", 
                            show_header=False)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="bold")
        
        summary_table.add_row("Total Items", str(self.stats.total_items))
        summary_table.add_row("Completed", f"[green]{self.stats.completed_items}[/green]")
        summary_table.add_row("Failed", f"[red]{self.stats.failed_items}[/red]")
        summary_table.add_row("Skipped", f"[yellow]{self.stats.skipped_items}[/yellow]")
        summary_table.add_row("Success Rate", f"{self.stats.success_rate:.1f}%")
        summary_table.add_row("Duration", f"{self.stats.duration:.2f}s")
        
        self.console.print()
        self.console.print(summary_table)
        
        # Show errors if any
        if self.stats.errors:
            self.console.print()
            error_panel = Panel(
                "\n".join(self.stats.errors[:10]) + 
                (f"\n... and {len(self.stats.errors) - 10} more" if len(self.stats.errors) > 10 else ""),
                title=f"❌ Issues ({len(self.stats.errors)})",
                border_style="red"
            )
            self.console.print(error_panel)


class FileProgressTracker:
    """
    Progress tracker for individual file operations.
    
    Useful for tracking progress within a single file operation,
    such as parsing large files or processing complex structures.
    """
    
    def __init__(self, 
                 console: Optional[Console] = None,
                 file_path: str = "",
                 operation_type: OperationType = OperationType.LOAD):
        """
        Initialize file progress tracker.
        
        Args:
            console: Rich Console instance
            file_path: Path to the file being processed
            operation_type: Type of operation being performed
        """
        self.console = console or Console()
        self.file_path = file_path
        self.operation_type = operation_type
        self.stats = OperationStats()
        
        self.progress: Optional[Progress] = None
        self.task: Optional[TaskID] = None
    
    @contextmanager
    def track_file_operation(self, 
                           total_steps: int,
                           operation_description: str = None):
        """
        Context manager for tracking a single file operation.
        
        Args:
            total_steps: Total number of processing steps
            operation_description: Description of the operation
            
        Yields:
            FileProgressTracker instance for updating progress
        """
        self.stats.total_items = total_steps
        self.stats.start_time = time.time()
        
        if not operation_description:
            operation_description = f"{self.operation_type.value.title()}ing file"
        
        file_name = self.file_path.split('/')[-1] if self.file_path else "file"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console,
                refresh_per_second=8
            ) as progress:
                self.progress = progress
                self.task = progress.add_task(
                    f"[cyan]{operation_description} • [dim]{file_name}[/dim]",
                    total=total_steps
                )
                
                yield self
                
        finally:
            self.stats.end_time = time.time()
    
    def update_step(self, 
                   step_description: str,
                   advance: int = 1):
        """
        Update the file processing step.
        
        Args:
            step_description: Description of the current step
            advance: Progress to advance
        """
        if not self.progress or self.task is None:
            return
        
        self.stats.completed_items += advance
        
        file_name = self.file_path.split('/')[-1] if self.file_path else "file"
        self.progress.update(
            self.task,
            advance=advance,
            description=f"[cyan]{step_description} • [dim]{file_name}[/dim]"
        )
    
    def add_error(self, error_message: str):
        """Record an error during file processing."""
        self.stats.failed_items += 1
        self.stats.errors.append(error_message)
