"""
Placeholder Module
Provides placeholder windows for features under construction.
"""

import tkinter as tk
from tkinter import ttk

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)


class PlaceholderWindow:
    """Generic placeholder window for features under construction."""
    
    def __init__(self, parent, title):
        """Initialize the placeholder window."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x400")
        self.window.minsize(500, 300)
        self.window.configure(bg=COLORS['bg_primary'])
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        center_window(self.window, 600, 400)
        
        # Configure styles
        configure_styles()
        
        # Build UI
        self._create_widgets(title)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_return)
        
    def _create_widgets(self, title):
        """Create all GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.window, bg=COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Content area (centered)
        content_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        content_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=title,
            font=('Segoe UI', 20, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(pady=(0, 30))
        
        # Construction icon (using text symbol)
        icon_label = tk.Label(
            content_frame,
            text="🚧",
            font=('Segoe UI', 48),
            bg=COLORS['bg_primary']
        )
        icon_label.pack(pady=(0, 20))
        
        # Under construction message
        message_label = tk.Label(
            content_frame,
            text="Under Construction",
            font=('Segoe UI', 18),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        message_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            content_frame,
            text="This feature is coming soon",
            font=('Segoe UI', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        subtitle_label.pack()
        
        # Footer with buttons
        footer_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Button container (right side)
        button_container = tk.Frame(footer_frame, bg=COLORS['bg_primary'])
        button_container.pack(side=tk.RIGHT)
        
        # Exit button
        create_styled_button(
            button_container,
            "Exit",
            self._on_exit,
            COLORS['exit_btn'],
            COLORS['exit_btn_hover']
        )

        # Return button
        create_styled_button(
            button_container,
            "Return",
            self._on_return,
            COLORS['return_btn'],
            COLORS['return_btn_hover']
        )

    def _on_return(self):
        """Handle return button click."""
        self.window.grab_release()
        self.window.destroy()

    def _on_exit(self):
        """Handle exit button click."""
        self.window.destroy()
        self.parent.quit()
        self.parent.destroy()