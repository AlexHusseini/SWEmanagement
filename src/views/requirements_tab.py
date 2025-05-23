import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.database import Database

class RequirementsTab:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.current_project_id = None
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create project selection frame
        self.create_project_selection()
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Add buttons
        self.add_btn = ttk.Button(self.buttons_frame, text="Add Requirement", command=self.show_add_requirement_dialog, state=tk.DISABLED)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(self.buttons_frame, text="Edit Requirement", command=self.show_edit_requirement_dialog, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(self.buttons_frame, text="Delete Requirement", command=self.delete_requirement, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Create requirements treeview
        self.create_requirements_treeview()
        
    def create_project_selection(self):
        # Create frame
        frame = ttk.Frame(self.main_frame)
        frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Add label
        ttk.Label(frame, text="Select Project:").pack(side=tk.LEFT, padx=5)
        
        # Add combobox
        self.project_combo = ttk.Combobox(frame, width=40, state="readonly")
        self.project_combo.pack(side=tk.LEFT, padx=5)
        
        # Bind event
        self.project_combo.bind("<<ComboboxSelected>>", self.on_project_selected)
        
        # Load projects
        self.load_projects()
        
    def load_projects(self):
        self.db.connect()
        projects = self.db.fetch_all("SELECT id, name FROM projects ORDER BY name")
        self.db.disconnect()
        
        self.projects = {p[1]: p[0] for p in projects}
        self.project_combo['values'] = list(self.projects.keys())
        
    def on_project_selected(self, event):
        selected_project = self.project_combo.get()
        if selected_project:
            self.current_project_id = self.projects[selected_project]
            self.load_requirements()
            self.add_btn['state'] = tk.NORMAL
        else:
            self.current_project_id = None
            self.add_btn['state'] = tk.DISABLED
            self.edit_btn['state'] = tk.DISABLED
            self.delete_btn['state'] = tk.DISABLED
        
    def create_requirements_treeview(self):
        # Create treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=("name", "type", "status", "description"), show="headings")
        self.tree.heading("name", text="Requirement Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("status", text="Status")
        self.tree.heading("description", text="Description")
        
        # Set column widths
        self.tree.column("name", width=200)
        self.tree.column("type", width=100)
        self.tree.column("status", width=100)
        self.tree.column("description", width=300)
        
        # Add scrollbars
        yscrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xscrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        
        # Pack widgets
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        yscrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        xscrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_requirement_selected)
        
    def on_requirement_selected(self, event):
        selected = self.tree.selection()
        if selected:
            self.edit_btn['state'] = tk.NORMAL
            self.delete_btn['state'] = tk.NORMAL
        else:
            self.edit_btn['state'] = tk.DISABLED
            self.delete_btn['state'] = tk.DISABLED
        
    def load_requirements(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.current_project_id:
            return
            
        # Connect to database and fetch requirements
        self.db.connect()
        requirements = self.db.fetch_all(
            "SELECT id, requirement_name, requirement_type, status, description FROM requirements WHERE project_id = %s ORDER BY requirement_name",
            (self.current_project_id,)
        )
        self.db.disconnect()
        
        # Add requirements to treeview
        for req in requirements:
            self.tree.insert("", tk.END, values=(req[1], req[2], req[3], req[4]), tags=(req[0],))
            
    def show_add_requirement_dialog(self):
        if not self.current_project_id:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Requirement")
        dialog.geometry("600x500")
        dialog.grab_set()  # Make dialog modal
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create form
        ttk.Label(main_frame, text="Requirement Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(main_frame, width=50)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        type_combo = ttk.Combobox(main_frame, width=47, values=["functional", "non-functional"], state="readonly")
        type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        type_combo.current(0)
        
        ttk.Label(main_frame, text="Status:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(main_frame, width=47, values=["pending", "in progress", "completed", "rejected"], state="readonly")
        status_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        status_combo.current(0)
        
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        desc_text = tk.Text(main_frame, width=50, height=10)
        desc_text.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        def save_requirement():
            name = name_entry.get()
            req_type = type_combo.get()
            status = status_combo.get()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Requirement name is required")
                return
                
            self.db.connect()
            query = """
                INSERT INTO requirements (project_id, requirement_name, description, requirement_type, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            if self.db.execute_query(query, (self.current_project_id, name, description, req_type, status)):
                self.load_requirements()
                dialog.destroy()
            self.db.disconnect()
            
        # Create button frame
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        ttk.Button(button_frame, text="Save", command=save_requirement).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def show_edit_requirement_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a requirement to edit")
            return
            
        requirement_id = self.tree.item(selected[0])["tags"][0]
        
        # Fetch requirement details
        self.db.connect()
        requirement = self.db.fetch_all(
            "SELECT requirement_name, description, requirement_type, status FROM requirements WHERE id = %s",
            (requirement_id,)
        )[0]
        self.db.disconnect()
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Requirement")
        dialog.geometry("600x500")
        dialog.grab_set()  # Make dialog modal
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create form
        ttk.Label(main_frame, text="Requirement Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(main_frame, width=50)
        name_entry.insert(0, requirement[0])
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        type_combo = ttk.Combobox(main_frame, width=47, values=["functional", "non-functional"], state="readonly")
        type_combo.set(requirement[2])
        type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="Status:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(main_frame, width=47, values=["pending", "in progress", "completed", "rejected"], state="readonly")
        status_combo.set(requirement[3])
        status_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        desc_text = tk.Text(main_frame, width=50, height=10)
        desc_text.insert("1.0", requirement[1] or "")
        desc_text.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        def save_changes():
            name = name_entry.get()
            req_type = type_combo.get()
            status = status_combo.get()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Requirement name is required")
                return
                
            self.db.connect()
            query = """
                UPDATE requirements 
                SET requirement_name = %s, description = %s, requirement_type = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            if self.db.execute_query(query, (name, description, req_type, status, requirement_id)):
                self.load_requirements()
                dialog.destroy()
            self.db.disconnect()
            
        # Create button frame
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def delete_requirement(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a requirement to delete")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this requirement?"):
            return
            
        requirement_id = self.tree.item(selected[0])["tags"][0]
        
        self.db.connect()
        if self.db.execute_query("DELETE FROM requirements WHERE id = %s", (requirement_id,)):
            self.load_requirements()
        self.db.disconnect() 