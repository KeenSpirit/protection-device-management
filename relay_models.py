"""
PowerFactory Relay Models Module
Displays relay model information from PowerFactory.
"""

import tkinter as tk
from tkinter import ttk

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)
from data_manager import get_data_manager, PF_TYPES_DIR


class RelayModelsWindow:
    """Window for displaying PowerFactory Relay Models data."""

    def __init__(self, parent):
        """Initialize the Relay Models window."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("PowerFactory Relay Models")
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
        self.relay_models = self.data_manager.get_relay_models()

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
            text="PowerFactory Relay Models",
            font=('Segoe UI', 24, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor='w')

        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Relay models available in PowerFactory for protection studies",
            font=('Segoe UI', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        subtitle_label.pack(anchor='w', pady=(5, 0))

        # Status message
        total_models = len(self.relay_models)
        validated_eql_count = sum(
            1 for rm in self.relay_models
            if rm.model_validated and rm.used_in_eql
        )
        with_mapping_count = sum(
            1 for rm in self.relay_models
            if rm.ips_mapping_file_exists
        )

        if total_models == 0:
            status_text = "No relay models found"
            status_color = COLORS['exit_btn']
        elif validated_eql_count == 0:
            status_text = f"{total_models} relay model(s) loaded, none validated for EQL use"
            status_color = '#f39c12'
        else:
            status_text = f"{validated_eql_count} of {total_models} EQL relay models validated | {with_mapping_count} with IPS mapping files"
            status_color = '#27ae60'

        status_label = tk.Label(
            header_frame,
            text=status_text,
            font=('Segoe UI', 11),
            fg=status_color,
            bg=COLORS['bg_primary']
        )
        status_label.pack(anchor='w', pady=(10, 0))

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
            'manufacturer',
            'model',
            'used_in_eql',
            'model_validated',
            'ips_mapping_file_exists'
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
            'manufacturer': ('Manufacturer', 180, 'w'),
            'model': ('Model', 180, 'w'),
            'used_in_eql': ('Used in EQL', 120, 'center'),
            'model_validated': ('Model Validated', 150, 'center'),
            'ips_mapping_file_exists': ('IPS Mapping File Exists', 350, 'w')
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

        # Configure row tags
        self.tree.tag_configure('oddrow', background=COLORS['row_odd'])
        self.tree.tag_configure('evenrow', background=COLORS['row_even'])
        self.tree.tag_configure('validated', background='#e8f5e9')  # Light green for validated
        self.tree.tag_configure('not_validated', background='#fdecea')  # Light red for not validated
        self.tree.tag_configure('has_mapping', background='#e3f2fd')  # Light blue for has mapping file

    def _populate_table(self):
        """Populate the table with relay model data."""
        for i, model in enumerate(self.relay_models):
            # Determine row tag based on validation and mapping status
            if model.model_validated and model.used_in_eql:
                tag = 'validated'
            elif model.used_in_eql and not model.model_validated:
                tag = 'not_validated'
            elif model.ips_mapping_file_exists:
                tag = 'has_mapping'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.tree.insert(
                '',
                tk.END,
                values=(
                    model.manufacturer,
                    model.model,
                    model.used_in_eql,
                    model.model_validated,
                    model.ips_mapping_file_exists
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

        # Status labels container (left side)
        status_container = tk.Frame(footer_frame, bg=COLORS['bg_primary'])
        status_container.pack(side=tk.LEFT)

        # Status label - record count
        total_models = len(self.relay_models)
        if total_models > 0:
            status_text = f"✓ {total_models} relay model(s) loaded"
            status_color = '#27ae60'
        else:
            status_text = "⚠ No relay models loaded"
            status_color = COLORS['exit_btn']

        status_label = tk.Label(
            status_container,
            text=status_text,
            font=('Segoe UI', 10),
            fg=status_color,
            bg=COLORS['bg_primary']
        )
        status_label.pack(anchor='w')

        # Last modified date label
        last_modified = self.data_manager.get_relay_models_last_modified()
        if last_modified:
            modified_label = tk.Label(
                status_container,
                text=f"pf_relay_models source data last updated on {last_modified}",
                font=('Segoe UI', 9),
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_primary']
            )
            modified_label.pack(anchor='w', pady=(2, 0))

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
    return get_data_manager().get_relay_models_summary_stats()