"""
PowerFactory Protection Device Management
Main application with landing page for navigating to different modules.
"""

import tkinter as tk
from tkinter import ttk

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)
from data_manager import get_data_manager
from ips_relay_patterns import IPSRelayPatternsWindow, get_summary_stats as get_ips_stats
from relay_models import RelayModelsWindow, get_summary_stats as get_relay_stats
from fuse_models import FuseModelsWindow, get_summary_stats as get_fuse_stats
from mapping_files import MappingFilesWindow, get_summary_stats as get_mapping_stats
from script_maintenance import ScriptMaintenanceWindow, get_summary_stats as get_maintenance_stats
from validation_suite import ValidationSuiteWindow


class LandingPage:
    """Main landing page for Protection Device Management."""

    def __init__(self, root):
        """Initialize the landing page."""
        self.root = root
        self.root.title("PowerFactory Protection Device Management")
        self.root.geometry("1400x700")
        self.root.minsize(1200, 600)
        self.root.configure(bg=COLORS['bg_primary'])

        # Center window
        center_window(self.root, 1400, 700)

        # Configure styles
        configure_styles()

        # Build UI
        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Create fixed footer first (pack at bottom)
        self._create_footer(self.root)

        # Main container with scrollbar support (above footer)
        scroll_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        scroll_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        main_canvas = tk.Canvas(scroll_container, bg=COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=main_canvas.yview)

        main_frame = tk.Frame(main_canvas, bg=COLORS['bg_primary'])

        main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind mousewheel
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Content container
        content_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Header
        self._create_header(content_frame)

        # Two-column sections container
        columns_frame = tk.Frame(content_frame, bg=COLORS['bg_primary'])
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Left column (sections 1-3)
        left_column = tk.Frame(columns_frame, bg=COLORS['bg_primary'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._create_section(
            left_column,
            "1. IPS Relay Patterns",
            "View and analyze protection relay patterns from IPS data.",
            "Open IPS Relay Patterns",
            self._open_ips_relay_patterns,
            get_ips_stats()
        )

        self._create_section(
            left_column,
            "2. PowerFactory Relay Models",
            "Manage relay models in PowerFactory.",
            "Open Relay Models",
            self._open_relay_models,
            get_relay_stats()
        )

        self._create_section(
            left_column,
            "3. PowerFactory Fuse Models",
            "Manage fuse models in PowerFactory.",
            "Open Fuse Models",
            self._open_fuse_models,
            get_fuse_stats()
        )

        # Right column (sections 4-6)
        right_column = tk.Frame(columns_frame, bg=COLORS['bg_primary'])
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self._create_section(
            right_column,
            "4. IPS to PowerFactory Mapping Files",
            "Configure mapping between IPS and PowerFactory data.",
            "Open Mapping Files",
            self._open_mapping_files,
            get_mapping_stats()
        )

        self._create_section(
            right_column,
            "5. IPS to PowerFactory Script Maintenance",
            "Maintain and configure automation scripts.",
            "Open Script Maintenance",
            self._open_script_maintenance,
            get_maintenance_stats()
        )

        self._create_section_no_status(
            right_column,
            "6. Relay and Mapping Validation Suite",
            "Guidance on validating relay models and mapping files.",
            "Open Validation Suite",
            self._open_validation_suite
        )

    def _create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        header_frame.pack(fill=tk.X)

        # Title
        title_label = tk.Label(
            header_frame,
            text="PowerFactory Protection Device Management",
            font=('Segoe UI', 26, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor='center')

        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Select a module below to get started",
            font=('Segoe UI', 12),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        subtitle_label.pack(anchor='center', pady=(8, 0))

    def _create_section(self, parent, title, description, button_text, button_command, summary_text):
        """Create a section card."""
        # Section container with border
        section_outer = tk.Frame(parent, bg=COLORS['section_border'])
        section_outer.pack(fill=tk.X, pady=(0, 15))

        section_frame = tk.Frame(
            section_outer,
            bg=COLORS['section_bg'],
            padx=20,
            pady=15
        )
        section_frame.pack(fill=tk.X, padx=2, pady=2)

        # Left side: Title, Description, Button
        left_frame = tk.Frame(section_frame, bg=COLORS['section_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Section title
        title_label = tk.Label(
            left_frame,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['section_bg'],
            anchor='w'
        )
        title_label.pack(fill=tk.X)

        # Description
        desc_label = tk.Label(
            left_frame,
            text=description,
            font=('Segoe UI', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['section_bg'],
            anchor='w'
        )
        desc_label.pack(fill=tk.X, pady=(5, 10))

        # Button
        btn = tk.Button(
            left_frame,
            text=button_text,
            font=('Segoe UI', 10),
            fg='white',
            bg=COLORS['header_bg'],
            activebackground=COLORS['accent'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=6,
            command=button_command
        )
        btn.pack(anchor='w')

        # Button hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['accent']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['header_bg']))

        # Right side: Status
        right_frame = tk.Frame(section_frame, bg=COLORS['section_bg'])
        right_frame.pack(side=tk.RIGHT, padx=(20, 0))

        # Status label
        summary_title = tk.Label(
            right_frame,
            text="Status",
            font=('Segoe UI', 10, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['section_bg']
        )
        summary_title.pack(anchor='e')

        # Summary value
        summary_value = tk.Label(
            right_frame,
            text=summary_text,
            font=('Segoe UI', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['section_bg'],
            justify=tk.RIGHT
        )
        summary_value.pack(anchor='e', pady=(3, 0))

    def _create_section_no_status(self, parent, title, description, button_text, button_command):
        """Create a section card without the Status field."""
        # Section container with border
        section_outer = tk.Frame(parent, bg=COLORS['section_border'])
        section_outer.pack(fill=tk.X, pady=(0, 15))

        section_frame = tk.Frame(
            section_outer,
            bg=COLORS['section_bg'],
            padx=20,
            pady=15
        )
        section_frame.pack(fill=tk.X, padx=2, pady=2)

        # Left side: Title, Description, Button
        left_frame = tk.Frame(section_frame, bg=COLORS['section_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Section title
        title_label = tk.Label(
            left_frame,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['section_bg'],
            anchor='w'
        )
        title_label.pack(fill=tk.X)

        # Description
        desc_label = tk.Label(
            left_frame,
            text=description,
            font=('Segoe UI', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['section_bg'],
            anchor='w'
        )
        desc_label.pack(fill=tk.X, pady=(5, 10))

        # Button
        btn = tk.Button(
            left_frame,
            text=button_text,
            font=('Segoe UI', 10),
            fg='white',
            bg=COLORS['header_bg'],
            activebackground=COLORS['accent'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=6,
            command=button_command
        )
        btn.pack(anchor='w')

        # Button hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['accent']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['header_bg']))

    def _create_footer(self, parent):
        """Create the footer section (fixed at bottom)."""
        # Separator line
        separator = tk.Frame(parent, bg=COLORS['border'], height=1)
        separator.pack(side=tk.BOTTOM, fill=tk.X)

        # Footer frame
        footer_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=40, pady=15)

        # Exit button
        create_styled_button(
            footer_frame,
            "Exit Application",
            self._on_exit,
            COLORS['exit_btn'],
            COLORS['exit_btn_hover'],
            side=tk.RIGHT
        )

        # Version label
        version_label = tk.Label(
            footer_frame,
            text="Version 1.0",
            font=('Segoe UI', 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        version_label.pack(side=tk.LEFT)

    def _open_ips_relay_patterns(self):
        """Open the IPS Relay Patterns window."""
        IPSRelayPatternsWindow(self.root)

    def _open_relay_models(self):
        """Open the Relay Models window."""
        RelayModelsWindow(self.root)

    def _open_fuse_models(self):
        """Open the Fuse Models window."""
        FuseModelsWindow(self.root)

    def _open_mapping_files(self):
        """Open the Mapping Files window."""
        MappingFilesWindow(self.root)

    def _open_script_maintenance(self):
        """Open the Script Maintenance window."""
        ScriptMaintenanceWindow(self.root)

    def _open_validation_suite(self):
        """Open the Validation Suite window."""
        ValidationSuiteWindow(self.root)

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

    # Initialize data manager - loads all data at startup
    print("Loading data sources...")
    data_manager = get_data_manager()
    print(f"  - Loaded {len(data_manager.get_relay_patterns())} relay patterns")
    print(f"  - Loaded {len(data_manager.get_mapping_files())} mapping files")
    print("Data loading complete.")

    app = LandingPage(root)
    root.mainloop()


if __name__ == "__main__":
    main()