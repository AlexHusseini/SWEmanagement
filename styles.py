"""
Styles Module for the Project Management System
This module provides styling constants and functions to improve the visual appearance
of the application.
"""

import tkinter as tk
from tkinter import ttk
import platform
import os

# Color Constants - Modern and Professional Color Scheme
COLORS = {
    'primary': '#3f51b5',       # Indigo - Headers, primary buttons
    'primary_light': '#757de8',  # Light Indigo - Hover states
    'primary_dark': '#002984',   # Dark Indigo - Selections
    'secondary': '#ff6f00',     # Orange - Accents, secondary buttons
    'secondary_light': '#ffa040', # Light Orange - Highlights
    'danger': '#f44336',        # Red - Warnings, deletes
    'success': '#4caf50',       # Green - Success messages
    'warning': '#ff9800',       # Amber - Caution alerts
    'info': '#2196f3',          # Blue - Info messages
    'gray_light': '#f5f5f5',    # Light Gray - Backgrounds
    'gray_medium': '#e0e0e0',   # Medium Gray - Borders, separators
    'gray_dark': '#757575',     # Dark Gray - Disabled items
    'text_primary': '#212121',  # Near Black - Primary text
    'text_secondary': '#757575', # Dark Gray - Secondary text
    'white': '#ffffff',         # White - Text on dark backgrounds
    'black': '#000000',         # Black - Text on light backgrounds
}

# Font Constants
FONTS = {
    'header_large': ('Segoe UI', 18, 'bold'),
    'header_medium': ('Segoe UI', 14, 'bold'),
    'header_small': ('Segoe UI', 12, 'bold'),
    'text_normal': ('Segoe UI', 10),
    'text_small': ('Segoe UI', 9),
    'text_bold': ('Segoe UI', 10, 'bold'),
    'text_italic': ('Segoe UI', 10, 'italic'),
    'monospace': ('Consolas', 10),
}

# Padding and Size Constants
PADDING = {
    'small': 5,
    'medium': 10,
    'large': 15,
    'xlarge': 20,
}

# Button sizes
BUTTON_SIZES = {
    'small': {'width': 8, 'padding': 2},
    'medium': {'width': 12, 'padding': 5},
    'large': {'width': 15, 'padding': 8},
}

def apply_styles(root):
    """Apply custom styles to the application"""
    style = ttk.Style()
    
    # Configure main theme
    if platform.system() == 'Windows':
        style.theme_use('vista')
    elif platform.system() == 'Darwin':  # macOS
        style.theme_use('clam')
    else:  # Linux and other
        style.theme_use('clam')
    
    # Configure TButton style
    style.configure('TButton', 
                    background=COLORS['primary'],
                    foreground=COLORS['primary'],
                    font=FONTS['text_normal'],
                    padding=6)
    
    # Primary button style
    style.configure('Primary.TButton',
                    background=COLORS['primary'],
                    foreground=COLORS['white'])
    
    style.map('Primary.TButton',
              background=[('active', COLORS['primary_light']),
                          ('disabled', COLORS['gray_medium'])],
              foreground=[('disabled', COLORS['gray_dark'])])
    
    # Secondary button style
    style.configure('Secondary.TButton',
                    background=COLORS['secondary'],
                    foreground=COLORS['white'])
    
    style.map('Secondary.TButton',
              background=[('active', COLORS['secondary_light']),
                          ('disabled', COLORS['gray_medium'])],
              foreground=[('disabled', COLORS['gray_dark'])])
    
    # Danger button style
    style.configure('Danger.TButton',
                    background=COLORS['danger'],
                    foreground=COLORS['white'])
    
    style.map('Danger.TButton',
              background=[('active', '#f77066'),  # Lighter red
                          ('disabled', COLORS['gray_medium'])],
              foreground=[('disabled', COLORS['gray_dark'])])
    
    # Success button style
    style.configure('Success.TButton',
                    background=COLORS['success'],
                    foreground=COLORS['white'])
    
    style.map('Success.TButton',
              background=[('active', '#5dbd61'),  # Lighter green
                          ('disabled', COLORS['gray_medium'])],
              foreground=[('disabled', COLORS['gray_dark'])])
    
    # Label styles
    style.configure('Header.TLabel', 
                    font=FONTS['header_medium'],
                    foreground=COLORS['primary_dark'])
    
    style.configure('SubHeader.TLabel', 
                    font=FONTS['header_small'],
                    foreground=COLORS['primary'])
    
    style.configure('Bold.TLabel',
                    font=FONTS['text_bold'])
    
    # Frame styles
    style.configure('Card.TFrame',
                    background=COLORS['white'],
                    relief=tk.RAISED,
                    borderwidth=1)
    
    style.configure('Header.TFrame',
                    background=COLORS['primary'],
                    relief=tk.FLAT)
    
    # Treeview styles
    style.configure('Treeview',
                    background=COLORS['white'],
                    foreground=COLORS['text_primary'],
                    fieldbackground=COLORS['white'],
                    font=FONTS['text_normal'])
    
    style.map('Treeview',
              background=[('selected', COLORS['primary_light'])],
              foreground=[('selected', COLORS['white'])])
    
    style.configure('Treeview.Heading',
                    background=COLORS['primary'],
                    foreground=COLORS['white'],
                    font=FONTS['text_bold'],
                    relief=tk.FLAT)
    
    style.map('Treeview.Heading',
              background=[('active', COLORS['primary_light'])])
    
    # Notebook styles
    style.configure('TNotebook',
                    background=COLORS['gray_light'],
                    tabmargins=[2, 5, 2, 0])
    
    style.configure('TNotebook.Tab',
                    background=COLORS['gray_medium'],
                    foreground=COLORS['text_primary'],
                    padding=[10, 4],
                    font=FONTS['text_normal'])
    
    style.map('TNotebook.Tab',
              background=[('selected', COLORS['primary']),
                          ('active', COLORS['primary_light'])],
              foreground=[('selected', COLORS['text_primary']),
                          ('active', COLORS['text_primary'])],
              font=[('selected', FONTS['text_bold'])])
    
    # Entry styles
    style.configure('TEntry',
                    fieldbackground=COLORS['white'],
                    foreground=COLORS['text_primary'],
                    padding=5)
    
    # Combobox styles
    style.configure('TCombobox',
                    fieldbackground=COLORS['white'],
                    foreground=COLORS['text_primary'],
                    padding=5)
    
    # Separator styles
    style.configure('TSeparator',
                    background=COLORS['gray_medium'])

def create_custom_button(master, text, command, style='Primary.TButton', **kwargs):
    """Create a custom styled button"""
    btn = ttk.Button(master, text=text, command=command, style=style, **kwargs)
    return btn

def create_title_label(master, text, **kwargs):
    """Create a title label with custom styling"""
    label = ttk.Label(master, text=text, style='Header.TLabel', **kwargs)
    return label

def create_subtitle_label(master, text, **kwargs):
    """Create a subtitle label with custom styling"""
    label = ttk.Label(master, text=text, style='SubHeader.TLabel', **kwargs)
    return label

def create_card_frame(master, **kwargs):
    """Create a card-like frame with shadow effect"""
    frame = ttk.Frame(master, style='Card.TFrame', **kwargs)
    return frame

def create_header_frame(master, **kwargs):
    """Create a header frame with distinct background"""
    frame = ttk.Frame(master, style='Header.TFrame', **kwargs)
    return frame

def flash_message(widget, original_bg, flash_color, times=3, delay=50):
    """Flash a widget by changing its background color temporarily
    
    Args:
        widget: The widget to flash
        original_bg: The original background color to return to
        flash_color: The color to flash with
        times: Number of flashes
        delay: Delay between color changes in milliseconds
    """
    if times > 0:
        current_bg = widget.cget('background')
        next_color = flash_color if current_bg == original_bg else original_bg
        widget.config(background=next_color)
        widget.after(delay, lambda: flash_message(widget, original_bg, flash_color, times-1, delay))
    else:
        widget.config(background=original_bg)

def create_dashboard_card(master, title, content, icon=None, bg_color=None):
    """Create a dashboard card with title, content and optional icon
    
    Args:
        master: Parent widget
        title: Card title
        content: Main content text
        icon: Optional icon (as PhotoImage)
        bg_color: Background color override
    
    Returns:
        Frame containing the card
    """
    bg = bg_color if bg_color else COLORS['white']
    
    card = ttk.Frame(master, style='Card.TFrame')
    card.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Title area
    title_frame = ttk.Frame(card, style='Header.TFrame')
    title_frame.pack(fill=tk.X)
    
    if icon:
        icon_label = ttk.Label(title_frame, image=icon, background=COLORS['primary'])
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    title_label = ttk.Label(title_frame, text=title, 
                           font=FONTS['header_small'],
                           foreground=COLORS['white'],
                           background=COLORS['primary'])
    title_label.pack(side=tk.LEFT, padx=10, pady=8)
    
    # Content area
    content_frame = ttk.Frame(card)
    content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    content_label = ttk.Label(content_frame, text=content,
                             font=FONTS['text_normal'],
                             wraplength=200)
    content_label.pack(padx=5, pady=5)
    
    return card

def load_project_icons():
    """
    Load and create common icons for the application
    Returns a dictionary of PhotoImage objects
    """
    icons = {}
    
    # Check if we have a suitable icons directory
    icon_paths = [
        os.path.join(os.path.dirname(__file__), 'icons'),
        os.path.join(os.path.dirname(__file__), 'assets', 'icons'),
    ]
    
    icon_dir = None
    for path in icon_paths:
        if os.path.exists(path) and os.path.isdir(path):
            icon_dir = path
            break
    
    if not icon_dir:
        return icons  # Return empty dict if no icons directory
        
    # Common icons
    icon_files = {
        'project': 'project.png',
        'task': 'task.png',
        'team': 'team.png',
        'risk': 'risk.png',
        'settings': 'settings.png',
        'logout': 'logout.png',
        'add': 'add.png',
        'edit': 'edit.png',
        'delete': 'delete.png',
        'save': 'save.png',
        'export': 'export.png',
    }
    
    # Try to load icons
    for name, filename in icon_files.items():
        try:
            path = os.path.join(icon_dir, filename)
            if os.path.exists(path):
                icons[name] = tk.PhotoImage(file=path)
        except Exception:
            # Skip if can't load
            pass
    
    return icons

# Example of usage:
if __name__ == "__main__":
    # Demo of the styles
    root = tk.Tk()
    root.title("Styles Demo")
    root.geometry("800x600")
    
    apply_styles(root)
    
    # Header
    header_frame = create_header_frame(root)
    header_frame.pack(fill=tk.X, padx=0, pady=0)
    
    header_label = ttk.Label(header_frame, text="Project Management System", 
                           font=FONTS['header_large'],
                           foreground=COLORS['white'],
                           background=COLORS['primary'])
    header_label.pack(padx=20, pady=15)
    
    # Main content
    content_frame = ttk.Frame(root)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Create some sample widgets to demonstrate styles
    create_title_label(content_frame, "Style Demonstration").pack(anchor='w', pady=10)
    create_subtitle_label(content_frame, "Button Styles").pack(anchor='w', pady=5)
    
    # Button frame
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    # Different button styles
    create_custom_button(button_frame, "Primary Button", lambda: None).pack(side=tk.LEFT, padx=5)
    create_custom_button(button_frame, "Secondary", lambda: None, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
    create_custom_button(button_frame, "Success", lambda: None, style='Success.TButton').pack(side=tk.LEFT, padx=5)
    create_custom_button(button_frame, "Danger", lambda: None, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
    
    # Card demo
    create_subtitle_label(content_frame, "Card Frames").pack(anchor='w', pady=10)
    
    cards_frame = ttk.Frame(content_frame)
    cards_frame.pack(fill=tk.X, pady=10)
    
    # Create sample cards
    card1 = create_dashboard_card(cards_frame, "Projects", "12 active projects")
    card1.pack(side=tk.LEFT, padx=10, pady=10)
    
    card2 = create_dashboard_card(cards_frame, "Tasks", "24 tasks pending")
    card2.pack(side=tk.LEFT, padx=10, pady=10)
    
    card3 = create_dashboard_card(cards_frame, "Team", "8 team members")
    card3.pack(side=tk.LEFT, padx=10, pady=10)
    
    # Treeview demo
    create_subtitle_label(content_frame, "Styled Treeview").pack(anchor='w', pady=10)
    
    tree_frame = ttk.Frame(content_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    tree = ttk.Treeview(tree_frame, columns=("Name", "Role", "Status"), show="headings", height=5)
    tree.heading("Name", text="Name")
    tree.heading("Role", text="Role")
    tree.heading("Status", text="Status")
    
    tree.column("Name", width=150)
    tree.column("Role", width=150)
    tree.column("Status", width=100)
    
    # Add some sample data
    tree.insert("", tk.END, values=("John Doe", "Project Manager", "Active"))
    tree.insert("", tk.END, values=("Jane Smith", "Developer", "Active"))
    tree.insert("", tk.END, values=("Mike Johnson", "Designer", "Inactive"))
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    # Run the demo
    root.mainloop() 