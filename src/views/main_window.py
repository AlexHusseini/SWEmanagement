import tkinter as tk
from tkinter import ttk
from .projects_tab import ProjectsTab
from .requirements_tab import RequirementsTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main content area
        self.create_content_area()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project")
        file_menu.add_command(label="Open Project")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Projects")
        view_menu.add_command(label="Requirements")
        view_menu.add_command(label="Effort Tracking")
        view_menu.add_command(label="Risk Management")
        
    def create_content_area(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add tabs
        self.projects_tab = ProjectsTab(self.notebook)
        self.requirements_tab = RequirementsTab(self.notebook)
        self.effort_tab = ttk.Frame(self.notebook)
        self.risks_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.projects_tab.main_frame, text="Projects")
        self.notebook.add(self.requirements_tab.main_frame, text="Requirements")
        self.notebook.add(self.effort_tab, text="Effort Tracking")
        self.notebook.add(self.risks_tab, text="Risk Management") 