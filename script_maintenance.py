"""
IPS to PowerFactory Script Maintenance Module
Displays script run logs and failed transfer details.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)
from data_manager import get_data_manager, LOGS_DIR


class ScriptMaintenanceWindow:
    """Window for IPS to PowerFactory Script Maintenance."""

    def __init__(self, parent):
        """Initialize the Script Maintenance window."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("IPS to PowerFactory Script Maintenance")
        self.window.geometry("1200x800")
        self.window.minsize(900, 600)
        self.window.configure(bg=COLORS['bg_primary'])

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center window
        center_window(self.window, 1200, 800)

        # Configure styles
        configure_styles()

        # Get data from data manager
        self.data_manager = get_data_manager()
        self.script_run_logs = self.data_manager.get_script_run_logs()
        self.failed_transfers = self.data_manager.get_failed_transfers()
        self.log_stats = self.data_manager.get_script_log_stats()

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

        # Scrollable content area for both tables
        self._create_scrollable_content(main_frame)

        # Footer section with buttons
        self._create_footer(main_frame)

    def _create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Title
        title_label = tk.Label(
            header_frame,
            text="IPS to PowerFactory Script Maintenance",
            font=('Segoe UI', 24, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor='w')

        # Directory location label
        location_label = tk.Label(
            header_frame,
            text="Location of script log files:",
            font=('Segoe UI', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        location_label.pack(anchor='w', pady=(10, 0))

        # Directory link (clickable)
        dir_link = tk.Label(
            header_frame,
            text=str(LOGS_DIR),
            font=('Segoe UI', 10, 'underline'),
            fg=COLORS['return_btn'],
            bg=COLORS['bg_primary'],
            cursor='hand2'
        )
        dir_link.pack(anchor='w')
        dir_link.bind('<Button-1>', lambda e: self._open_directory(LOGS_DIR))
        dir_link.bind('<Enter>', lambda e: dir_link.configure(fg=COLORS['return_btn_hover']))
        dir_link.bind('<Leave>', lambda e: dir_link.configure(fg=COLORS['return_btn']))

        # Status row with message and delete button
        status_row = tk.Frame(header_frame, bg=COLORS['bg_primary'])
        status_row.pack(fill=tk.X, pady=(10, 0))

        # Status message (left side)
        total_runs = self.log_stats.get('total_runs', 0)
        total_failures = self.log_stats.get('total_failures', 0)

        if total_runs == 0:
            status_text = "No script runs found in log file"
            status_color = COLORS['exit_btn']
        else:
            # Calculate overall success rate
            total_transfers = sum(log.num_transfers for log in self.script_run_logs)
            if total_transfers > 0:
                overall_success = ((total_transfers - total_failures) / total_transfers) * 100
                status_text = f"{total_runs} script run(s) logged | {total_failures} failed transfer(s) | {overall_success:.1f}% overall success rate"
                if overall_success >= 90:
                    status_color = '#27ae60'  # Green for good success rate
                elif overall_success >= 70:
                    status_color = '#f39c12'  # Orange for moderate success rate
                else:
                    status_color = COLORS['exit_btn']  # Red for low success rate
            else:
                status_text = f"{total_runs} script run(s) logged | No transfers recorded"
                status_color = '#f39c12'

        self.status_label = tk.Label(
            status_row,
            text=status_text,
            font=('Segoe UI', 11),
            fg=status_color,
            bg=COLORS['bg_primary']
        )
        self.status_label.pack(side=tk.LEFT)

        # Delete Log File Contents button (right side)
        delete_btn = tk.Button(
            status_row,
            text="Delete Log File Contents",
            font=('Segoe UI', 10),
            fg='white',
            bg=COLORS['exit_btn'],
            activebackground=COLORS['exit_btn_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=4,
            command=self._on_delete_log_contents
        )
        delete_btn.pack(side=tk.RIGHT)

        # Button hover effects
        delete_btn.bind('<Enter>', lambda e: delete_btn.configure(bg=COLORS['exit_btn_hover']))
        delete_btn.bind('<Leave>', lambda e: delete_btn.configure(bg=COLORS['exit_btn']))

    def _on_delete_log_contents(self):
        """Handle delete log file contents button click."""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete all contents of the log file?\n\n"
            "This action cannot be undone.",
            icon='warning',
            parent=self.window
        )

        if result:
            try:
                # Get the log file path
                log_file_path = LOGS_DIR / "ips_to_pf"

                # Clear the file contents by opening in write mode
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    pass  # Opening in 'w' mode and closing clears the file

                # Refresh the data manager
                self.data_manager.refresh_data()

                # Update local data references
                self.script_run_logs = self.data_manager.get_script_run_logs()
                self.failed_transfers = self.data_manager.get_failed_transfers()
                self.log_stats = self.data_manager.get_script_log_stats()

                # Refresh the tables
                self._refresh_tables()

                # Update status message
                self.status_label.config(
                    text="No script runs found in log file",
                    fg=COLORS['exit_btn']
                )

                # Update footer status
                self._update_footer_status()

                # Show success message
                messagebox.showinfo(
                    "Success",
                    "Log file contents have been deleted successfully.",
                    parent=self.window
                )

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to delete log file contents:\n{str(e)}",
                    parent=self.window
                )

    def _refresh_tables(self):
        """Refresh both tables after data change."""
        # Clear and repopulate script runs table
        for item in self.runs_tree.get_children():
            self.runs_tree.delete(item)
        self._populate_script_runs_table()

        # Clear and repopulate failed transfers table
        for item in self.failures_tree.get_children():
            self.failures_tree.delete(item)
        self._populate_failed_transfers_table()

        # Update record count labels
        self.runs_count_label.config(text=f"Showing {len(self.script_run_logs)} script run(s)")
        self.failures_count_label.config(text=f"Showing {len(self.failed_transfers)} failed transfer(s)")

    def _update_footer_status(self):
        """Update the footer status label."""
        total_runs = len(self.script_run_logs)
        total_failures = len(self.failed_transfers)

        if total_runs > 0:
            status_text = f"✓ {total_runs} script run(s) | {total_failures} failed transfer(s)"
            status_color = '#27ae60' if total_failures == 0 else '#f39c12'
        else:
            status_text = "⚠ No log data loaded"
            status_color = COLORS['exit_btn']

        self.footer_status_label.config(text=status_text, fg=status_color)

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

    def _create_scrollable_content(self, parent):
        """Create content area containing both tables."""
        # Simple frame container (no outer scrollbar needed - tables have their own)
        content_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Store reference for compatibility
        self.content_canvas = None

        # Create Table 1: Log of all Script Runs
        self._create_script_runs_table(content_frame)

        # Spacer between tables
        spacer = tk.Frame(content_frame, bg=COLORS['bg_primary'], height=20)
        spacer.pack(fill=tk.X)

        # Create Table 2: Log of All Failed Device Transfers
        self._create_failed_transfers_table(content_frame)

    def _create_script_runs_table(self, parent):
        """Create the Script Runs table."""
        # Table heading
        heading_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        heading_frame.pack(fill=tk.X, pady=(0, 10))

        heading_label = tk.Label(
            heading_frame,
            text="Log of All Script Runs",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        heading_label.pack(anchor='w')

        # Card-like container for table
        table_container = ttk.Frame(parent, style="Card.TFrame")
        table_container.pack(fill=tk.X, pady=(0, 5))

        # Add subtle border effect
        border_frame = tk.Frame(
            table_container,
            bg=COLORS['border'],
            highlightthickness=0
        )
        border_frame.pack(fill=tk.X, padx=1, pady=1)

        inner_frame = tk.Frame(border_frame, bg=COLORS['bg_secondary'])
        inner_frame.pack(fill=tk.X)

        # Define columns
        columns = (
            'timestamp',
            'substation',
            'num_transfers',
            'success_percentage'
        )

        # Calculate row height based on number of entries (max 10 visible rows)
        num_rows = min(len(self.script_run_logs), 10) if self.script_run_logs else 3
        tree_height = num_rows

        # Create treeview
        self.runs_tree = ttk.Treeview(
            inner_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            selectmode='browse',
            height=tree_height
        )

        # Configure column headings and widths
        column_config = {
            'timestamp': ('Timestamp', 200, 'w'),
            'substation': ('Substation', 150, 'center'),
            'num_transfers': ('Number of Transfers', 180, 'center'),
            'success_percentage': ('Percentage Successful Transfers', 250, 'center')
        }

        for col, (heading, width, anchor) in column_config.items():
            self.runs_tree.heading(col, text=heading, anchor='center')
            self.runs_tree.column(col, width=width, anchor=anchor, minwidth=80)

        # Create scrollbar for table
        runs_scrollbar = ttk.Scrollbar(
            inner_frame,
            orient=tk.VERTICAL,
            command=self.runs_tree.yview
        )
        self.runs_tree.configure(yscrollcommand=runs_scrollbar.set)

        # Pack table and scrollbar
        self.runs_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        runs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure row tags
        self.runs_tree.tag_configure('oddrow', background=COLORS['row_odd'])
        self.runs_tree.tag_configure('evenrow', background=COLORS['row_even'])
        self.runs_tree.tag_configure('low_success', background='#fdecea')  # Light red for low success
        self.runs_tree.tag_configure('high_success', background='#e8f5e9')  # Light green for high success

        # Populate table
        self._populate_script_runs_table()

        # Record count label
        self.runs_count_label = tk.Label(
            parent,
            text=f"Showing {len(self.script_run_logs)} script run(s)",
            font=('Segoe UI', 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        self.runs_count_label.pack(anchor='w', pady=(2, 0))

    def _populate_script_runs_table(self):
        """Populate the script runs table with data."""
        for i, log in enumerate(self.script_run_logs):
            # Determine row tag based on success percentage
            if log.success_percentage >= 90:
                tag = 'high_success'
            elif log.success_percentage < 50:
                tag = 'low_success'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            # Format success percentage
            success_str = f"{log.success_percentage:.1f}%"

            self.runs_tree.insert(
                '',
                tk.END,
                values=(
                    log.timestamp,
                    log.substation,
                    log.num_transfers,
                    success_str
                ),
                tags=(tag,)
            )

    def _create_failed_transfers_table(self, parent):
        """Create the Failed Transfers table."""
        # Table heading
        heading_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        heading_frame.pack(fill=tk.X, pady=(10, 10))

        heading_label = tk.Label(
            heading_frame,
            text="Log of All Failed Device Transfers",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        heading_label.pack(anchor='w')

        # Card-like container for table
        table_container = ttk.Frame(parent, style="Card.TFrame")
        table_container.pack(fill=tk.X, pady=(0, 5))

        # Add subtle border effect
        border_frame = tk.Frame(
            table_container,
            bg=COLORS['border'],
            highlightthickness=0
        )
        border_frame.pack(fill=tk.X, padx=1, pady=1)

        inner_frame = tk.Frame(border_frame, bg=COLORS['bg_secondary'])
        inner_frame.pack(fill=tk.X)

        # Define columns
        columns = (
            'timestamp',
            'substation',
            'device_name',
            'result'
        )

        # Calculate row height based on number of entries (max 15 visible rows)
        num_rows = min(len(self.failed_transfers), 15) if self.failed_transfers else 3
        tree_height = num_rows

        # Create treeview
        self.failures_tree = ttk.Treeview(
            inner_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            selectmode='browse',
            height=tree_height
        )

        # Configure column headings and widths
        column_config = {
            'timestamp': ('Timestamp', 200, 'w'),
            'substation': ('Substation', 120, 'center'),
            'device_name': ('Device Name', 250, 'w'),
            'result': ('Result', 300, 'w')
        }

        for col, (heading, width, anchor) in column_config.items():
            self.failures_tree.heading(col, text=heading, anchor='center')
            self.failures_tree.column(col, width=width, anchor=anchor, minwidth=80)

        # Create scrollbar for table
        failures_scrollbar = ttk.Scrollbar(
            inner_frame,
            orient=tk.VERTICAL,
            command=self.failures_tree.yview
        )
        self.failures_tree.configure(yscrollcommand=failures_scrollbar.set)

        # Pack table and scrollbar
        self.failures_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        failures_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure row tags
        self.failures_tree.tag_configure('oddrow', background=COLORS['row_odd'])
        self.failures_tree.tag_configure('evenrow', background=COLORS['row_even'])
        self.failures_tree.tag_configure('no_match', background='#fdecea')  # Light red for failures
        self.failures_tree.tag_configure('not_mapped', background='#fff3cd')  # Light yellow for not mapped

        # Populate table
        self._populate_failed_transfers_table()

        # Record count label
        self.failures_count_label = tk.Label(
            parent,
            text=f"Showing {len(self.failed_transfers)} failed transfer(s)",
            font=('Segoe UI', 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        self.failures_count_label.pack(anchor='w', pady=(2, 0))

    def _populate_failed_transfers_table(self):
        """Populate the failed transfers table with data."""
        for i, transfer in enumerate(self.failed_transfers):
            # Determine row tag based on result type
            result_lower = transfer.result.lower()
            if 'not mapped' in result_lower:
                tag = 'not_mapped'
            elif 'failed' in result_lower or 'match' in result_lower:
                tag = 'no_match'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.failures_tree.insert(
                '',
                tk.END,
                values=(
                    transfer.timestamp,
                    transfer.substation,
                    transfer.device_name,
                    transfer.result
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
        total_runs = len(self.script_run_logs)
        total_failures = len(self.failed_transfers)

        if total_runs > 0:
            status_text = f"✓ {total_runs} script run(s) | {total_failures} failed transfer(s)"
            status_color = '#27ae60' if total_failures == 0 else '#f39c12'
        else:
            status_text = "⚠ No log data loaded"
            status_color = COLORS['exit_btn']

        self.footer_status_label = tk.Label(
            footer_frame,
            text=status_text,
            font=('Segoe UI', 10),
            fg=status_color,
            bg=COLORS['bg_primary']
        )
        self.footer_status_label.pack(side=tk.LEFT)

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
    return get_data_manager().get_script_maintenance_summary_stats()