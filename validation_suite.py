"""
Relay and Mapping Validation Suite Module
Provides guidance on validating PowerFactory relay models and mapping files.
"""

import tkinter as tk
from tkinter import ttk

from common import (
    COLORS, configure_styles, center_window, create_styled_button
)


class ValidationSuiteWindow:
    """Window for Relay Model and Mapping File Validation guidance."""

    def __init__(self, parent):
        """Initialize the Validation Suite window."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Relay Model and Mapping File Validation")
        self.window.geometry("900x650")
        self.window.minsize(800, 550)
        self.window.configure(bg=COLORS['bg_primary'])

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center window
        center_window(self.window, 900, 650)

        # Configure styles
        configure_styles()

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

        # Content section (scrollable)
        self._create_content(main_frame)

        # Footer section with buttons
        self._create_footer(main_frame)

    def _create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Title
        title_label = tk.Label(
            header_frame,
            text="Relay Model and Mapping File Validation",
            font=('Segoe UI', 24, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor='w')

        # Introduction text
        intro_text = (
            "This section provides high level guidance on how to validate correct "
            "functionality of PowerFactory relay models and IPS-to-PowerFactory mapping files."
        )
        intro_label = tk.Label(
            header_frame,
            text=intro_text,
            font=('Segoe UI', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            wraplength=850,
            justify=tk.LEFT
        )
        intro_label.pack(anchor='w', pady=(10, 0))

    def _create_content(self, parent):
        """Create the main content section with scrollbar."""
        # Card-like container
        content_container = ttk.Frame(parent, style="Card.TFrame")
        content_container.pack(fill=tk.BOTH, expand=True)

        # Add subtle border effect
        border_frame = tk.Frame(
            content_container,
            bg=COLORS['border'],
            highlightthickness=0
        )
        border_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Canvas for scrolling
        canvas = tk.Canvas(border_frame, bg=COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(border_frame, orient=tk.VERTICAL, command=canvas.yview)

        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_secondary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add content to scrollable frame
        self._add_validation_content(scrollable_frame)

    def _add_validation_content(self, parent):
        """Add the validation procedure content."""
        content_frame = tk.Frame(parent, bg=COLORS['bg_secondary'], padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Relay Model Validation Procedure section
        section_title = tk.Label(
            content_frame,
            text="Relay Model Validation Procedure:",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary']
        )
        section_title.pack(anchor='w', pady=(0, 15))

        # Procedure steps
        steps = [
            ("1)", "Configure the relay in the model with validated settings."),
            ("2)", "Execute a short circuit command"),
            ("3)", "Check if the relay trips as expected"),
            ("4)", "Provide a trace of all input and output signals for each relay block:"),
        ]

        for number, text in steps:
            step_frame = tk.Frame(content_frame, bg=COLORS['bg_secondary'])
            step_frame.pack(anchor='w', fill=tk.X, pady=(0, 8))

            number_label = tk.Label(
                step_frame,
                text=number,
                font=('Segoe UI', 11),
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary'],
                width=4,
                anchor='w'
            )
            number_label.pack(side=tk.LEFT)

            text_label = tk.Label(
                step_frame,
                text=text,
                font=('Segoe UI', 11),
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary'],
                anchor='w',
                justify=tk.LEFT
            )
            text_label.pack(side=tk.LEFT, fill=tk.X)

        # Sub-steps for step 4
        sub_steps = [
            ("4.1)",
             'Open the dialog of the relay object and press the "Contents" button to access a browser containing the relay blocks.'),
            ("4.2)", "Select the relevant block and enable the detailed mode."),
            ("4.3)", "Switch to the flexible data page."),
            ("4.4)", 'Click on the button "Variable Selection".'),
            ("4.5)", 'Select the Variable Set "Signals".'),
            ("4.6)", "Add the result variable you want to access and press OK."),
        ]

        for number, text in sub_steps:
            substep_frame = tk.Frame(content_frame, bg=COLORS['bg_secondary'])
            substep_frame.pack(anchor='w', fill=tk.X, pady=(0, 6))

            # Indent for sub-steps
            indent_label = tk.Label(
                substep_frame,
                text="",
                font=('Segoe UI', 11),
                bg=COLORS['bg_secondary'],
                width=4
            )
            indent_label.pack(side=tk.LEFT)

            number_label = tk.Label(
                substep_frame,
                text=number,
                font=('Segoe UI', 11),
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_secondary'],
                width=5,
                anchor='w'
            )
            number_label.pack(side=tk.LEFT)

            text_label = tk.Label(
                substep_frame,
                text=text,
                font=('Segoe UI', 11),
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_secondary'],
                anchor='w',
                justify=tk.LEFT,
                wraplength=700
            )
            text_label.pack(side=tk.LEFT, fill=tk.X)

        # Mapping File Validation Procedure section
        section_title2 = tk.Label(
            content_frame,
            text="Mapping File Validation Procedure:",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary']
        )
        section_title2.pack(anchor='w', pady=(30, 10))

        # Note text
        note_label = tk.Label(
            content_frame,
            text="(This should only be performed on relay models that have been validated.)",
            font=('Segoe UI', 11, 'italic'),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            anchor='w'
        )
        note_label.pack(anchor='w', pady=(0, 15))

        # Mapping validation steps
        mapping_steps = [
            ("1)", "Using the ips_to_pf.py script and the mapping file, apply known relay settings from a test relay setting ID."),
            ("2)", "Verify that all relay attributes match the relay setting ID."),
        ]

        for number, text in mapping_steps:
            step_frame = tk.Frame(content_frame, bg=COLORS['bg_secondary'])
            step_frame.pack(anchor='w', fill=tk.X, pady=(0, 8))

            number_label = tk.Label(
                step_frame,
                text=number,
                font=('Segoe UI', 11),
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary'],
                width=4,
                anchor='w'
            )
            number_label.pack(side=tk.LEFT)

            text_label = tk.Label(
                step_frame,
                text=text,
                font=('Segoe UI', 11),
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary'],
                anchor='w',
                justify=tk.LEFT,
                wraplength=700
            )
            text_label.pack(side=tk.LEFT, fill=tk.X)

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

    def _on_return(self):
        """Handle return button click."""
        self.window.grab_release()
        self.window.destroy()

    def _on_exit(self):
        """Handle exit button click."""
        self.window.destroy()
        self.parent.quit()
        self.parent.destroy()