"""
Style Integration - Helper module to apply styles to the main application
This module provides functions to integrate the styles.py module with the existing application.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the parent directory to sys.path to ensure we can import styles
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import styles
    STYLES_AVAILABLE = True
except ImportError:
    print("Warning: styles module not found. Falling back to default styles.")
    STYLES_AVAILABLE = False

def apply_styles_to_application(root):
    """Apply the custom styles to the main application"""
    if not STYLES_AVAILABLE:
        return
    
    # Apply basic styles
    styles.apply_styles(root)
    
    # Return the styles module for further customization
    return styles

def style_login_window(login_window):
    """Apply styles to the login window"""
    if not STYLES_AVAILABLE:
        return
    
    root = login_window.root
    
    # Apply background colors
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.configure(style='Card.TFrame')
    
    # Style the title
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Label) and "Project Management System" in widget.cget('text'):
            widget.configure(style='Header.TLabel', foreground=styles.COLORS['primary'])
    
    # Style buttons in login tab
    try:
        # Attempt to access widgets in the login tab
        login_button = login_window.login_button
        login_button.configure(style='Primary.TButton')
        
        if hasattr(login_window, 'skip_button'):
            skip_button = login_window.skip_button
            skip_button.configure(style='Secondary.TButton')
    except (AttributeError, NameError):
        # Handle case where these attributes might not exist
        pass
    
    # Add a header
    frame = login_window.root
    header_frame = styles.create_header_frame(frame)
    header_frame.pack(fill=tk.X, side=tk.TOP)
    
    header_label = ttk.Label(
        header_frame,
        text="Project Management System", 
        font=styles.FONTS['header_large'],
        foreground=styles.COLORS['white'],
        background=styles.COLORS['primary']
    )
    header_label.pack(padx=20, pady=15)
    
    # Move the header to the top of the window
    header_frame.pack_forget()
    header_frame.pack(fill=tk.X, side=tk.TOP, before=frame.winfo_children()[0])

def style_main_app(app):
    """Apply styles to the main application"""
    if not STYLES_AVAILABLE:
        return
    
    # Style the notebook tabs
    if hasattr(app, 'notebook'):
        app.notebook.configure(style='TNotebook')
    
    # Style buttons
    for widget in app.root.winfo_descendants():
        if isinstance(widget, ttk.Button):
            if "Delete" in widget.cget('text'):
                widget.configure(style='Danger.TButton')
            elif "Save" in widget.cget('text') or "Add" in widget.cget('text'):
                widget.configure(style='Primary.TButton')
            elif "Edit" in widget.cget('text') or "View" in widget.cget('text'):
                widget.configure(style='Secondary.TButton')
    
    # Style treeviews
    for widget in app.root.winfo_descendants():
        if isinstance(widget, ttk.Treeview):
            widget.configure(style='Treeview')
    
    # Add a header
    header_frame = styles.create_header_frame(app.root)
    header_frame.pack(fill=tk.X, side=tk.TOP)
    
    header_label = ttk.Label(
        header_frame,
        text="Project Management System", 
        font=styles.FONTS['header_large'],
        foreground=styles.COLORS['white'],
        background=styles.COLORS['primary']
    )
    header_label.pack(padx=20, pady=15)
    
    # Move the header to the top of the window
    header_frame.pack_forget()
    header_frame.pack(fill=tk.X, side=tk.TOP, before=app.root.winfo_children()[0])
    
    # Add some styling to the status bar if it exists
    try:
        status_frame = ttk.Frame(app.root, style='Card.TFrame')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        status_label = ttk.Label(
            status_frame, 
            text=f"Logged in as: {app.current_user['username']} ({app.current_user['role']})",
            font=styles.FONTS['text_small'],
            padding=5
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        app.status_frame = status_frame
        app.status_label = status_label
    except (AttributeError, NameError):
        # Handle case where these attributes might not exist
        pass

def patch_main_application():
    """
    Patch the main application to use the styles
    This function should be called before the application is initialized
    """
    if not STYLES_AVAILABLE:
        return
    
    # Get the original main module
    try:
        # This assumes we're in the same directory as the main application
        import Group_1_Project_Management_System as app_module
        
        # Store original initialization methods
        original_login_init = app_module.LoginWindow.__init__
        
        # Define patched methods
        def patched_login_init(self, root, on_login_success, skip_allowed=True):
            # Call original init
            original_login_init(self, root, on_login_success, skip_allowed)
            
            # Apply styles
            style_login_window(self)
        
        # Apply the patches
        app_module.LoginWindow.__init__ = patched_login_init
        
        print("Styles integration: Main application patched successfully!")
        return True
    except (ImportError, AttributeError) as e:
        print(f"Styles integration error: {e}")
        return False

# Apply the styles when this module is imported
apply_result = patch_main_application()

if __name__ == "__main__":
    print("Style Integration Module")
    print(f"Styles available: {STYLES_AVAILABLE}")
    print(f"Patch result: {apply_result}")
    
    # Test the styles with a small demo
    if STYLES_AVAILABLE:
        root = tk.Tk()
        root.title("Style Integration Test")
        root.geometry("400x300")
        
        # Apply styles
        apply_styles_to_application(root)
        
        # Create a header
        header_frame = styles.create_header_frame(root)
        header_frame.pack(fill=tk.X)
        
        header_label = ttk.Label(
            header_frame,
            text="Style Integration Test", 
            font=styles.FONTS['header_large'],
            foreground=styles.COLORS['white'],
            background=styles.COLORS['primary']
        )
        header_label.pack(padx=20, pady=15)
        
        # Add some content
        content_frame = ttk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(content_frame, text="Style integration successful!", style='Header.TLabel').pack(pady=10)
        
        styles.create_custom_button(content_frame, "Primary Button", lambda: None).pack(pady=10)
        styles.create_custom_button(content_frame, "Secondary Button", lambda: None, style='Secondary.TButton').pack(pady=10)
        
        root.mainloop() 