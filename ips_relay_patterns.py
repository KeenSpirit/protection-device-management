"""
IPS Relay Patterns Module
Displays summary of protection device patterns from IPS data.
Supports filtering by SEQ and Regional data sources.
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

        # Checkbox state variables (both checked by default)
        self.seq_var = tk.BooleanVar(value=True)
        self.regional_var = tk.BooleanVar(value=True)

        # Build UI
        self._create_widgets()

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_return)

    def _get_filtered_data(self):
        """Get relay patterns based on current checkbox selections."""
        return self.data_manager.get_relay_patterns(
            include_seq=self.seq_var.get(),
            include_regional=self.regional_var.get()
        )

    def _get_total_records(self):
        """Get total records based on current checkbox selections."""
        return self.data_manager.get_ips_total_records(
            include_seq=self.seq_var.get(),
            include_regional=self.regional_var.get()
        )

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

        # Subtitle row with record count and checkboxes
        subtitle_frame = tk.Frame(header_frame, bg=COLORS['bg_primary'])
        subtitle_frame.pack(fill=tk.X, pady=(5, 0))

        # Subtitle with record count (left side)
        self.subtitle_label = tk.Label(
            subtitle_frame,
            text="",
            font=('Segoe UI', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        self.subtitle_label.pack(side=tk.LEFT)

        # Checkbox container (right side)
        checkbox_frame = tk.Frame(subtitle_frame, bg=COLORS['bg_primary'])
        checkbox_frame.pack(side=tk.RIGHT)

        # Regional checkbox
        regional_cb = tk.Checkbutton(
            checkbox_frame,
            text="Regional",
            variable=self.regional_var,
            font=('Segoe UI', 10),
            bg=COLORS['bg_primary'],
            activebackground=COLORS['bg_primary'],
            command=self._on_filter_change
        )
        regional_cb.pack(side=tk.RIGHT, padx=(10, 0))

        # SEQ checkbox
        seq_cb = tk.Checkbutton(
            checkbox_frame,
            text="SEQ",
            variable=self.seq_var,
            font=('Segoe UI', 10),
            bg=COLORS['bg_primary'],
            activebackground=COLORS['bg_primary'],
            command=self._on_filter_change
        )
        seq_cb.pack(side=tk.RIGHT)

        # Update subtitle text
        self._update_subtitle()

    def _update_subtitle(self):
        """Update the subtitle text based on current filter."""
        data = self._get_filtered_data()
        record_count = len(data)
        self.subtitle_label.config(text=f"Showing {record_count} unique protection patterns")

    def _on_filter_change(self):
        """Handle checkbox state change - refresh the table."""
        self._update_subtitle()
        self._refresh_table()
        self._update_footer_status()

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
            'source',
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
            'pattern': ('Pattern', 250, 'w'),
            'asset': ('Asset', 180, 'w'),
            'eql_population': ('EQL Population', 120, 'center'),
            'source': ('Source', 80, 'center'),
            'powerfactory_model': ('PowerFactory Model', 180, 'center'),
            'mapping_file': ('Mapping File', 180, 'w')
        }

        for col, (heading, width, anchor) in column_config.items():
            self.tree.heading(col, text=heading, anchor='center')
            self.tree.column(col, width=width, anchor=anchor, minwidth=60)

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
        self.tree.tag_configure('seq_row', background='#e3f2fd')  # Light blue for SEQ
        self.tree.tag_configure('regional_row', background='#fff3e0')  # Light orange for Regional

    def _populate_table(self):
        """Populate the table with summary data."""
        data = self._get_filtered_data()
        for i, row in enumerate(data):
            # Use source-based coloring
            if row.source == 'SEQ':
                tag = 'seq_row'
            elif row.source == 'Regional':
                tag = 'regional_row'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.tree.insert(
                '',
                tk.END,
                values=(
                    row.pattern,
                    row.asset,
                    row.eql_population,
                    row.source,
                    row.powerfactory_model,
                    row.mapping_file
                ),
                tags=(tag,)
            )

    def _refresh_table(self):
        """Clear and repopulate the table based on current filters."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Repopulate
        self._populate_table()

    def _create_footer(self, parent):
        """Create the footer section with buttons."""
        self.footer_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        self.footer_frame.pack(fill=tk.X, pady=(15, 0))

        # Button container (right side)
        button_container = tk.Frame(self.footer_frame, bg=COLORS['bg_primary'])
        button_container.pack(side=tk.RIGHT)

        # Exit button
        create_styled_button(
            button_container,
            "Exit Application",
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

        # Status label container (left side)
        self.status_container = tk.Frame(self.footer_frame, bg=COLORS['bg_primary'])
        self.status_container.pack(side=tk.LEFT)

        # Create status label
        self._update_footer_status()

    def _update_footer_status(self):
        """Update the footer status label."""
        # Clear existing status labels
        for widget in self.status_container.winfo_children():
            widget.destroy()

        total_records = self._get_total_records()

        if total_records == 0:
            status_text = "⚠ No data loaded"
            status_color = COLORS['exit_btn']
        else:
            status_text = f"✓ {total_records:,} total records processed"
            status_color = '#27ae60'

        status_label = tk.Label(
            self.status_container,
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