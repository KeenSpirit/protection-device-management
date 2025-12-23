"""
IPS to PowerFactory Mapping Files Module
Displays mapping file information linked from type_mapping.csv.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)
from data_manager import get_data_manager, MAPPING_DIR


class MappingFilesWindow:
    """Window for displaying IPS to PowerFactory Mapping Files."""

    def __init__(self, parent):
        """Initialize the Mapping Files window."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("IPS to PowerFactory Mapping Files")
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
        self.mapping_data = self.data_manager.get_mapping_files()
        self.parse_stats = self.data_manager.get_mapping_parse_stats()

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
            text="IPS to PowerFactory Mapping Files",
            font=('Segoe UI', 24, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor='w')

        # Directory location label
        location_label = tk.Label(
            header_frame,
            text="Location of relay mapping files and type_mapping file:",
            font=('Segoe UI', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        location_label.pack(anchor='w', pady=(10, 0))

        # Directory link (clickable)
        dir_link = tk.Label(
            header_frame,
            text=str(MAPPING_DIR),
            font=('Segoe UI', 10, 'underline'),
            fg=COLORS['return_btn'],
            bg=COLORS['bg_primary'],
            cursor='hand2'
        )
        dir_link.pack(anchor='w')
        dir_link.bind('<Button-1>', lambda e: self._open_directory(MAPPING_DIR))
        dir_link.bind('<Enter>', lambda e: dir_link.configure(fg=COLORS['return_btn_hover']))
        dir_link.bind('<Leave>', lambda e: dir_link.configure(fg=COLORS['return_btn']))

        # Status message
        total = self.parse_stats['total']
        with_mappings = self.parse_stats['success']

        if total == 0:
            status_text = "No CSV files found in mapping directory"
            status_color = COLORS['exit_btn']
        elif with_mappings == total:
            status_text = f"All {total} mapping files have type mappings defined"
            status_color = '#27ae60'
        elif with_mappings == 0:
            status_text = f"{total} mapping files found, none have type mappings defined"
            status_color = '#f39c12'
        else:
            status_text = f"{with_mappings} of {total} mapping files have type mappings defined"
            status_color = '#f39c12'

        status_label = tk.Label(
            header_frame,
            text=status_text,
            font=('Segoe UI', 11),
            fg=status_color,
            bg=COLORS['bg_primary']
        )
        status_label.pack(anchor='w', pady=(10, 0))

        # Conditional help text - only show if some files don't have type mappings
        if total > 0 and with_mappings < total:
            help_label = tk.Label(
                header_frame,
                text="If a mapping file has no type_mapping defined, check that it is correctly configured in the type_mapping.csv file.",
                font=('Segoe UI', 10),
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_primary']
            )
            help_label.pack(anchor='w', pady=(5, 0))

    def _open_directory(self, path):
        """Open the directory in file explorer."""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', str(path)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(path)])
            else:  # Linux
                subprocess.run(['xdg-open', str(path)])
        except Exception as e:
            print(f"Could not open directory: {e}")

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
            'map_name',
            'ips_patterns',
            'pf_models',
            'validated'
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
            'map_name': ('Map Name', 300, 'w'),
            'ips_patterns': ('IPS Relay Pattern', 320, 'w'),
            'pf_models': ('PowerFactory Relay Model', 320, 'w'),
            'validated': ('Mapping File Validated', 150, 'center')
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
        self.tree.tag_configure('no_mapping', background='#fdecea')  # Light red for no mappings

    def _populate_table(self):
        """Populate the table with mapping data."""
        for i, row in enumerate(self.mapping_data):
            # Join multiple values with comma and space
            ips_patterns_str = ', '.join(row.ips_patterns) if row.ips_patterns else ''
            pf_models_str = ', '.join(row.pf_models) if row.pf_models else ''

            # Use different tag for rows without any mappings
            if not row.ips_patterns and not row.pf_models:
                tag = 'no_mapping'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.tree.insert(
                '',
                tk.END,
                values=(
                    row.filename,
                    ips_patterns_str,
                    pf_models_str,
                    row.validated
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

        # Status label (left side)
        total_files = len(self.mapping_data)
        if total_files > 0:
            status_text = f"✓ {total_files} mapping file(s) loaded"
            status_color = '#27ae60'
        else:
            status_text = "⚠ No mapping files loaded"
            status_color = COLORS['exit_btn']

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
    return get_data_manager().get_mapping_summary_stats()