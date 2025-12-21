"""
Protection Device Management
A GUI application for viewing and managing protection device data.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from pathlib import Path
import sys

# Configuration
SOURCE_DIR = Path(r"E:\Programming\_python_work\protection-device-management\Data sources\Queries")


class ProtectionDeviceApp:
    """Main application class for Protection Device Management GUI."""

    # Color scheme
    COLORS = {
        'bg_primary': '#f5f6fa',
        'bg_secondary': '#ffffff',
        'accent': '#2c3e50',
        'accent_hover': '#34495e',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'border': '#dcdde1',
        'header_bg': '#3498db',
        'header_fg': '#ffffff',
        'row_even': '#ffffff',
        'row_odd': '#f8f9fa',
        'exit_btn': '#e74c3c',
        'exit_btn_hover': '#c0392b',
    }

    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Protection Device Management")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)
        self.root.configure(bg=self.COLORS['bg_primary'])

        # Center window on screen
        self._center_window()

        # Configure styles
        self._configure_styles()

        # Load and process data
        self.data = self._load_data()
        self.summary_data = self._create_summary()

        # Build UI
        self._create_widgets()

    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def _configure_styles(self):
        """Configure ttk styles for a modern look."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Treeview styling
        self.style.configure(
            "Custom.Treeview",
            background=self.COLORS['bg_secondary'],
            foreground=self.COLORS['text_primary'],
            fieldbackground=self.COLORS['bg_secondary'],
            borderwidth=0,
            font=('Segoe UI', 10),
            rowheight=30
        )

        self.style.configure(
            "Custom.Treeview.Heading",
            background=self.COLORS['header_bg'],
            foreground=self.COLORS['header_fg'],
            font=('Segoe UI', 10, 'bold'),
            borderwidth=0,
            relief='flat'
        )

        self.style.map(
            "Custom.Treeview.Heading",
            background=[('active', self.COLORS['accent'])]
        )

        self.style.map(
            "Custom.Treeview",
            background=[('selected', self.COLORS['header_bg'])],
            foreground=[('selected', self.COLORS['header_fg'])]
        )

        # Frame styling
        self.style.configure(
            "Card.TFrame",
            background=self.COLORS['bg_secondary']
        )

        self.style.configure(
            "Main.TFrame",
            background=self.COLORS['bg_primary']
        )

    def _load_data(self):
        """Load data from the CSV file."""
        csv_path = SOURCE_DIR / "Report-Cache-ProtectionSettingIDs-EX.csv"

        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            return df
        except FileNotFoundError:
            messagebox.showerror(
                "File Not Found",
                f"Could not find the data file at:\n{csv_path}\n\n"
                "Please ensure SOURCE_DIR is configured correctly."
            )
            return pd.DataFrame()
        except Exception as e:
            messagebox.showerror(
                "Error Loading Data",
                f"An error occurred while loading the data:\n{str(e)}"
            )
            return pd.DataFrame()

    def _create_summary(self):
        """Create summary data from the loaded CSV."""
        if self.data.empty:
            return []

        # Get unique pattern names while preserving first occurrence order
        unique_patterns = self.data['patternname'].unique()

        summary = []
        for pattern in unique_patterns:
            # Filter rows for this pattern
            pattern_rows = self.data[self.data['patternname'] == pattern]

            # Get first matching asset name
            first_asset = pattern_rows['assetname'].iloc[0]

            # Count occurrences (EQL Population)
            count = len(pattern_rows)

            summary.append({
                'pattern': pattern,
                'asset': first_asset,
                'eql_population': count,
                'powerfactory_model': '',  # Placeholder for future
                'mapping_file': ''  # Placeholder for future
            })

        # Sort by EQL Population from largest to smallest
        summary.sort(key=lambda x: x['eql_population'], reverse=True)

        return summary

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header section
        self._create_header(main_frame)

        # Table section
        self._create_table(main_frame)

        # Footer section with buttons
        self._create_footer(main_frame)

    def _create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Title
        title_label = tk.Label(
            header_frame,
            text="Protection Device Summary",
            font=('Segoe UI', 24, 'bold'),
            fg=self.COLORS['accent'],
            bg=self.COLORS['bg_primary']
        )
        title_label.pack(anchor='w')

        # Subtitle with record count
        record_count = len(self.summary_data)
        subtitle_label = tk.Label(
            header_frame,
            text=f"Showing {record_count} unique protection patterns",
            font=('Segoe UI', 11),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['bg_primary']
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
            bg=self.COLORS['border'],
            highlightthickness=0
        )
        border_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        inner_frame = tk.Frame(border_frame, bg=self.COLORS['bg_secondary'])
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
            'mapping_file': ('Mapping File', 200, 'center')
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
        self.tree.tag_configure('oddrow', background=self.COLORS['row_odd'])
        self.tree.tag_configure('evenrow', background=self.COLORS['row_even'])

    def _populate_table(self):
        """Populate the table with summary data."""
        for i, row in enumerate(self.summary_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert(
                '',
                tk.END,
                values=(
                    row['pattern'],
                    row['asset'],
                    row['eql_population'],
                    row['powerfactory_model'],
                    row['mapping_file']
                ),
                tags=(tag,)
            )

    def _create_footer(self, parent):
        """Create the footer section with buttons."""
        footer_frame = tk.Frame(parent, bg=self.COLORS['bg_primary'])
        footer_frame.pack(fill=tk.X, pady=(15, 0))

        # Exit button with custom styling
        self.exit_btn = tk.Button(
            footer_frame,
            text="Exit",
            font=('Segoe UI', 11),
            fg='white',
            bg=self.COLORS['exit_btn'],
            activebackground=self.COLORS['exit_btn_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=8,
            command=self._on_exit
        )
        self.exit_btn.pack(side=tk.RIGHT)

        # Hover effects
        self.exit_btn.bind('<Enter>', self._on_exit_hover)
        self.exit_btn.bind('<Leave>', self._on_exit_leave)

        # Status label (left side)
        if self.data.empty:
            status_text = "⚠ No data loaded"
            status_color = self.COLORS['exit_btn']
        else:
            total_records = len(self.data)
            status_text = f"✓ {total_records:,} total records processed"
            status_color = '#27ae60'

        status_label = tk.Label(
            footer_frame,
            text=status_text,
            font=('Segoe UI', 10),
            fg=status_color,
            bg=self.COLORS['bg_primary']
        )
        status_label.pack(side=tk.LEFT)

    def _on_exit_hover(self, event):
        """Handle exit button hover."""
        self.exit_btn.configure(bg=self.COLORS['exit_btn_hover'])

    def _on_exit_leave(self, event):
        """Handle exit button leave."""
        self.exit_btn.configure(bg=self.COLORS['exit_btn'])

    def _on_exit(self):
        """Handle exit button click."""
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point for the application."""
    root = tk.Tk()

    # Set application icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except tk.TclError:
        pass  # Icon not available

    app = ProtectionDeviceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()