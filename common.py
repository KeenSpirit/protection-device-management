"""
Common utilities and styles for Protection Device Management.
Shared across all modules.
"""

import tkinter as tk
from tkinter import ttk


# Color scheme used throughout the application
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
    'return_btn': '#3498db',
    'return_btn_hover': '#2980b9',
    'section_bg': '#ffffff',
    'section_border': '#3498db',
}


def configure_styles():
    """Configure ttk styles for a modern look."""
    style = ttk.Style()
    style.theme_use('clam')

    # Treeview styling
    style.configure(
        "Custom.Treeview",
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_primary'],
        fieldbackground=COLORS['bg_secondary'],
        borderwidth=0,
        font=('Segoe UI', 10),
        rowheight=30
    )

    style.configure(
        "Custom.Treeview.Heading",
        background=COLORS['header_bg'],
        foreground=COLORS['header_fg'],
        font=('Segoe UI', 10, 'bold'),
        borderwidth=0,
        relief='flat'
    )

    style.map(
        "Custom.Treeview.Heading",
        background=[('active', COLORS['accent'])]
    )

    style.map(
        "Custom.Treeview",
        background=[('selected', COLORS['header_bg'])],
        foreground=[('selected', COLORS['header_fg'])]
    )

    # Frame styling
    style.configure(
        "Card.TFrame",
        background=COLORS['bg_secondary']
    )

    style.configure(
        "Main.TFrame",
        background=COLORS['bg_primary']
    )

    return style


def center_window(window, width=None, height=None):
    """Center a window on the screen."""
    window.update_idletasks()
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


def create_styled_button(parent, text, command, bg_color, hover_color, side=tk.RIGHT):
    """Create a styled button with hover effects."""
    btn = tk.Button(
        parent,
        text=text,
        font=('Segoe UI', 11),
        fg='white',
        bg=bg_color,
        activebackground=hover_color,
        activeforeground='white',
        relief='flat',
        cursor='hand2',
        padx=30,
        pady=8,
        command=command
    )

    btn.bind('<Enter>', lambda e: btn.configure(bg=hover_color))
    btn.bind('<Leave>', lambda e: btn.configure(bg=bg_color))

    if side:
        btn.pack(side=side, padx=(10, 0))

    return btn