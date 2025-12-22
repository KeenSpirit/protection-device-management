"""
IPS Relay Patterns Module
Displays summary of protection device patterns from IPS data.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)
from data_manager import get_data_manager


class IPSRelayPatternsWindow:
    """Window for displaying IPS Relay Patterns data."""

    def __init__(self, parent):
        """Initialize the IPS Relay Patterns window."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("IPS Relay Patterns")
        self.window.geometry("1200x700")
        self.window.minsize(900, 500)
        self.window.configure(bg=COLORS['bg_primary'])

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center window
        center_window(self.window, 1200, 700)

        # Configure styles
        configure_styles()

        # Get data from data manager
        self.data_manager = get_data_manager()
        self.summary_data = self.data_manager.get_relay_patterns()
        self.total_records = self.data_manager.get_ips_total_records()

        # Build UI
        self._create_widgets()

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_return)

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.window, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header section
        self._create_header(main_frame)

        # Table section
        self._create_table(main_frame)

        # Footer section with buttons
        self._create_footer(main_frame)

    def _create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Title
        title_label = tk.Label(
            header_frame,
            text="IPS Relay Patterns Summary",
            font=('Segoe UI', 24, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor='w')

        # Subtitle with record count
        record_count = len(self.summary_data)
        subtitle_label = tk.Label(
            header_frame,
            text=f"Showing {record_count} unique protection patterns",
            font=('Segoe UI', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        subtitle_label.pack(anchor='w', pady=(5, 0))

    def _create_table(self, parent):
        """Create the main table with scrollbar."""
        # Card-like container for table
        table_container = ttk.Frame(parent, style="Card.TFrame")
        table_container.pack(fill=tk.BOTH, expand=True)

        # Add subtle border effect
        border_frame = tk.Frame(
            table_container,
            bg=COLORS['border'],
            highlightthickness=0
        )
        border_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        inner_frame = tk.Frame(border_frame, bg=COLORS['bg_secondary'])
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # Define columns
        columns = (
            'pattern',
            'asset',
            'eql_population',
            'powerfactory_model',
            'mapping_file'
        )

        # Create treeview
        self.tree = ttk.Treeview(
            inner_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            selectmode='browse'
        )

        # Configure column headings and widths
        column_config = {
            'pattern': ('Pattern', 300, 'w'),
            'asset': ('Asset', 200, 'w'),
            'eql_population': ('EQL Population', 120, 'center'),
            'powerfactory_model': ('PowerFactory Model', 200, 'center'),
            'mapping_file': ('Mapping File', 200, 'w')
        }

        for col, (heading, width, anchor) in column_config.items():
            self.tree.heading(col, text=heading, anchor='center')
            self.tree.column(col, width=width, anchor=anchor, minwidth=80)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            inner_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack table and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate table
        self._populate_table()

        # Bind alternating row colors
        self.tree.tag_configure('oddrow', background=COLORS['row_odd'])
        self.tree.tag_configure('evenrow', background=COLORS['row_even'])

    def _populate_table(self):
        """Populate the table with summary data."""
        for i, row in enumerate(self.summary_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert(
                '',
                tk.END,
                values=(
                    row.pattern,
                    row.asset,
                    row.eql_population,
                    row.powerfactory_model,
                    row.mapping_file
                ),
                tags=(tag,)
            )

    def _create_footer(self, parent):
        """Create the footer section with buttons."""
        footer_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        footer_frame.pack(fill=tk.X, pady=(15, 0))

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

        # Status label (left side)
        if self.total_records == 0:
            status_text = "⚠ No data loaded"
            status_color = COLORS['exit_btn']
        else:
            status_text = f"✓ {self.total_records:,} total records processed"
            status_color = '#27ae60'

        status_label = tk.Label(
            footer_frame,
            text=status_text,
            font=('Segoe UI', 10),
            fg=status_color,
            bg=COLORS['bg_primary']
        )
        status_label.pack(side=tk.LEFT)

    def _on_return(self):
        """Handle return button click."""
        self.window.grab_release()
        self.window.destroy()

    def _on_exit(self):
        """Handle exit button click."""
        self.window.destroy()
        self.parent.quit()
        self.parent.destroy()


def get_summary_stats():
    """Get summary statistics for the landing page."""
    return get_data_manager().get_ips_summary_stats()